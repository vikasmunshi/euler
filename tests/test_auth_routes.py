#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Integration tests for the SRP login endpoints + gating middleware.

Drives the real aiohttp app end to end, using the Python :class:`SrpClient` as a
stand-in for the browser (the JS client mirrors it, checked separately by the
reference vectors). The session cookie is set ``Secure``, which aiohttp's test
client will not replay over http, so we forward it explicitly.
"""
from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase

from solver.web.auth import policy, routes
from solver.web.auth.pending import PendingStore
from solver.web.auth.remember import RememberStore
from solver.web.auth.routes import auth_middleware, setup_auth
from solver.web.auth.srp import SrpClient, SrpToken
from solver.web.auth.users import UserStore

_EMAIL = 'user@example.com'
_PASSWORD = 'correct horse battery staple'


class AuthRoutesTests(AioHTTPTestCase):
    async def get_application(self) -> web.Application:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        store = UserStore(Path(tmp.name) / 'users.json')
        store.register(_EMAIL, SrpToken.create(_EMAIL, _PASSWORD))
        self.pending = PendingStore(Path(tmp.name) / 'pending.json')
        self.remember = RememberStore(Path(tmp.name) / 'remember.json', b'\x00' * 32,
                                      policy.REMEMBER_TTL_SECONDS)
        app = web.Application(middlewares=[auth_middleware])
        with patch('solver.web.auth.routes.load_or_create_secret', return_value=b'\x00' * 32):
            setup_auth(app)                     # patched so it doesn't write keys/.session-secret
        app[routes.USERS] = store               # temp stores instead of config paths
        app[routes.PENDING_REG] = self.pending
        app[routes.REMEMBER] = self.remember
        app.router.add_get('/protected', self._protected)
        return app

    async def _protected(self, request: web.Request) -> web.Response:
        return web.Response(text='secret')

    async def _login(self, email: str, password: str,
                     remember: bool = False) -> tuple[SrpClient, web.HTTPException | object]:
        challenge = await self.client.post('/auth/challenge', json={'email': email})
        data = await challenge.json()
        client = SrpClient(email, password)
        m1 = client.process_challenge(bytes.fromhex(data['salt']), int(data['B'], 16))
        verify = await self.client.post('/auth/verify', json={
            'email': email, 'A': format(client.public, 'x'), 'M1': m1.hex(), 'remember': remember})
        return client, verify

    @staticmethod
    def _cookie_header(response: object) -> dict[str, str]:
        morsel = response.cookies.get(policy.SESSION_COOKIE)  # type: ignore[attr-defined]
        return {'Cookie': f'{policy.SESSION_COOKIE}={morsel.value}'} if morsel else {}

    async def test_protected_requires_auth(self) -> None:
        resp = await self.client.get('/protected')
        self.assertEqual(resp.status, 401)

    async def test_successful_login_grants_access(self) -> None:
        client, verify = await self._login(_EMAIL, _PASSWORD)
        self.assertEqual(verify.status, 200)
        body = await verify.json()
        self.assertTrue(client.verify_session(bytes.fromhex(body['M2'])))  # mutual auth
        headers = self._cookie_header(verify)
        self.assertTrue(headers, 'session cookie should be set')
        prot = await self.client.get('/protected', headers=headers)
        self.assertEqual(prot.status, 200)
        self.assertEqual(await prot.text(), 'secret')

    async def test_wrong_password_denied(self) -> None:
        _client, verify = await self._login(_EMAIL, 'the wrong password entirely')
        self.assertEqual(verify.status, 401)
        self.assertFalse(self._cookie_header(verify))

    async def test_unknown_email_is_decoy_then_denied(self) -> None:
        challenge = await self.client.post('/auth/challenge', json={'email': 'ghost@nowhere.test'})
        self.assertEqual(challenge.status, 200)          # indistinguishable from a real user
        data = await challenge.json()
        self.assertEqual(len(bytes.fromhex(data['salt'])), 16)
        client = SrpClient('ghost@nowhere.test', 'whatever')
        m1 = client.process_challenge(bytes.fromhex(data['salt']), int(data['B'], 16))
        verify = await self.client.post(
            '/auth/verify', json={'email': 'ghost@nowhere.test', 'A': format(client.public, 'x'), 'M1': m1.hex()})
        self.assertEqual(verify.status, 401)

    async def test_decoy_salt_is_stable_per_email(self) -> None:
        first = await (await self.client.post('/auth/challenge', json={'email': 'ghost@x.test'})).json()
        second = await (await self.client.post('/auth/challenge', json={'email': 'ghost@x.test'})).json()
        self.assertEqual(first['salt'], second['salt'])  # no salt-changes enumeration oracle

    async def test_verify_without_challenge_denied(self) -> None:
        client = SrpClient(_EMAIL, _PASSWORD)
        verify = await self.client.post(
            '/auth/verify', json={'email': _EMAIL, 'A': format(client.public, 'x'), 'M1': '00' * 32})
        self.assertEqual(verify.status, 401)

    async def test_logout_clears_session(self) -> None:
        _client, verify = await self._login(_EMAIL, _PASSWORD)
        headers = self._cookie_header(verify)
        logout = await self.client.get('/logout', headers=headers, allow_redirects=False)
        self.assertEqual(logout.status, 302)
        prot = await self.client.get('/protected', headers=headers)
        self.assertEqual(prot.status, 401)               # session destroyed server-side

    async def test_disabled_user_denied(self) -> None:
        self.app[routes.USERS].set_disabled(_EMAIL, True)
        _client, verify = await self._login(_EMAIL, _PASSWORD)
        self.assertEqual(verify.status, 401)

    async def test_invited_user_cannot_login(self) -> None:
        self.app[routes.USERS].invite('invited@nowhere.test')   # disabled, no verifier
        _client, verify = await self._login('invited@nowhere.test', 'anything long enough')
        self.assertEqual(verify.status, 401)

    async def test_registration_flow_creates_active_user(self) -> None:
        email, password = 'newuser@nowhere.test', 'a brand new password'
        self.app[routes.USERS].invite(email)
        link_token = self.pending.invite(email, 'register')     # admin `users add`

        validate = await self.client.post('/register/validate', json={'token': link_token})
        self.assertEqual(validate.status, 200)                  # non-consuming pre-check
        self.assertEqual((await validate.json())['email'], email)  # token binds the email

        srp = SrpToken.create(email, password)                  # browser derives salt+verifier
        complete = await self.client.post('/register/complete', json={
            'token': link_token, 'salt': srp.salt.hex(), 'verifier': format(srp.verifier, 'x')})
        self.assertEqual(complete.status, 200)
        self.assertTrue(self.app[routes.USERS].is_active(email))

        _client, verify = await self._login(email, password)    # can now log in
        self.assertEqual(verify.status, 200)

    async def test_register_validate_rejects_bad_token(self) -> None:
        resp = await self.client.post('/register/validate', json={'token': 'bogus'})
        self.assertEqual(resp.status, 401)

    async def test_register_complete_rejects_bad_token(self) -> None:
        email = 'newuser@nowhere.test'
        self.app[routes.USERS].invite(email)
        self.pending.invite(email, 'register')                  # a real token exists…
        srp = SrpToken.create(email, 'a brand new password')
        resp = await self.client.post('/register/complete', json={  # …but the wrong one is sent
            'token': 'wrong', 'salt': srp.salt.hex(), 'verifier': format(srp.verifier, 'x')})
        self.assertEqual(resp.status, 401)
        self.assertFalse(self.app[routes.USERS].is_active(email))

    async def test_register_token_is_single_use(self) -> None:
        email = 'newuser@nowhere.test'
        self.app[routes.USERS].invite(email)
        link_token = self.pending.invite(email, 'register')
        srp = SrpToken.create(email, 'a brand new password')
        body = {'token': link_token, 'salt': srp.salt.hex(), 'verifier': format(srp.verifier, 'x')}
        first = await self.client.post('/register/complete', json=body)
        self.assertEqual(first.status, 200)
        second = await self.client.post('/register/complete', json=body)  # consumed → gone
        self.assertEqual(second.status, 401)

    async def test_remember_me_sets_cookie_only_when_requested(self) -> None:
        _c, without = await self._login(_EMAIL, _PASSWORD, remember=False)
        self.assertNotIn(policy.REMEMBER_COOKIE, without.cookies)
        _c, with_remember = await self._login(_EMAIL, _PASSWORD, remember=True)
        self.assertIn(policy.REMEMBER_COOKIE, with_remember.cookies)

    async def test_remember_cookie_promotes_to_session(self) -> None:
        _c, verify = await self._login(_EMAIL, _PASSWORD, remember=True)
        remember = verify.cookies[policy.REMEMBER_COOKIE].value
        # a request with ONLY the remember cookie (no session) is promoted...
        prot = await self.client.get('/protected', headers={'Cookie': f'{policy.REMEMBER_COOKIE}={remember}'})
        self.assertEqual(prot.status, 200)
        # ...and issued a fresh session plus a rotated remember cookie
        self.assertIn(policy.SESSION_COOKIE, prot.cookies)
        self.assertIn(policy.REMEMBER_COOKIE, prot.cookies)
        self.assertNotEqual(prot.cookies[policy.REMEMBER_COOKIE].value, remember)

    async def test_logout_revokes_remember(self) -> None:
        _c, verify = await self._login(_EMAIL, _PASSWORD, remember=True)
        remember = verify.cookies[policy.REMEMBER_COOKIE].value
        session = verify.cookies[policy.SESSION_COOKIE].value
        await self.client.get('/logout', allow_redirects=False, headers={
            'Cookie': f'{policy.SESSION_COOKIE}={session}; {policy.REMEMBER_COOKIE}={remember}'})
        # the remember cookie no longer promotes after logout
        prot = await self.client.get('/protected', headers={'Cookie': f'{policy.REMEMBER_COOKIE}={remember}'})
        self.assertEqual(prot.status, 401)

    async def test_logout_closes_web_shells(self) -> None:
        _c, verify = await self._login(_EMAIL, _PASSWORD)
        session = verify.cookies[policy.SESSION_COOKIE].value

        class _FakeWS:
            def __init__(self) -> None:
                self.closed = False

            async def close(self, *, message: bytes = b'') -> None:
                self.closed = True

        fake = _FakeWS()
        self.app[routes.WS_CONNECTIONS].setdefault(_EMAIL, set()).add(fake)  # type: ignore[arg-type]
        await self.client.get('/logout', allow_redirects=False,
                              headers={'Cookie': f'{policy.SESSION_COOKIE}={session}'})
        self.assertTrue(fake.closed)                                  # the shell socket was closed
        self.assertNotIn(_EMAIL, self.app[routes.WS_CONNECTIONS])     # and its registry entry dropped

    async def test_rate_limit_returns_429(self) -> None:
        for _ in range(policy.AUTH_RATE_MAX):
            ok = await self.client.post('/auth/challenge', json={'email': _EMAIL})
            self.assertEqual(ok.status, 200)
        blocked = await self.client.post('/auth/challenge', json={'email': _EMAIL})
        self.assertEqual(blocked.status, 429)

    async def test_security_headers_present(self) -> None:
        resp = await self.client.get('/login')
        self.assertEqual(resp.headers.get('X-Content-Type-Options'), 'nosniff')
        self.assertEqual(resp.headers.get('X-Frame-Options'), 'SAMEORIGIN')
        self.assertEqual(resp.headers.get('Referrer-Policy'), 'no-referrer')

    async def test_password_reset_overwrites_verifier(self) -> None:
        # `users reset` mints a secure link; the browser then re-registers with a new password.
        link_token = self.pending.invite(_EMAIL, 'reset')
        new_password = 'a totally different passphrase'
        token = SrpToken.create(_EMAIL, new_password)
        complete = await self.client.post('/register/complete', json={
            'token': link_token, 'salt': token.salt.hex(), 'verifier': format(token.verifier, 'x')})
        self.assertEqual(complete.status, 200)
        _c, with_new = await self._login(_EMAIL, new_password)
        self.assertEqual(with_new.status, 200)
        _c, with_old = await self._login(_EMAIL, _PASSWORD)
        self.assertEqual(with_old.status, 401)

    async def test_whoami_returns_email_and_profile(self) -> None:
        _c, verify = await self._login(_EMAIL, _PASSWORD)
        session = verify.cookies[policy.SESSION_COOKIE].value
        resp = await self.client.get('/whoami', headers={'Cookie': f'{policy.SESSION_COOKIE}={session}'})
        self.assertEqual(resp.status, 200)
        body = await resp.json()
        self.assertEqual(body['email'], _EMAIL)
        self.assertEqual(body['profile'], 'user')        # setUp registers _EMAIL with the default profile

    async def test_whoami_requires_auth(self) -> None:
        self.assertEqual((await self.client.get('/whoami')).status, 401)

    async def test_authz_reflects_user_profile(self) -> None:
        _c, verify = await self._login(_EMAIL, _PASSWORD)     # a 'user'
        session = verify.cookies[policy.SESSION_COOKIE].value
        resp = await self.client.get('/authz?cmd=evaluate&cmd=users&cmd=unlisted-cmd',
                                     headers={'Cookie': f'{policy.SESSION_COOKIE}={session}'})
        self.assertEqual(resp.status, 200)
        # evaluate is granted to user; users is admin-only; an unlisted command is admin-only
        self.assertEqual(await resp.json(), {'evaluate': True, 'users': False, 'unlisted-cmd': False})

    async def test_authz_restricts_guest(self) -> None:
        self.app[routes.USERS].register('guest@nowhere.test',
                                        SrpToken.create('guest@nowhere.test', _PASSWORD), 'guest')
        _c, verify = await self._login('guest@nowhere.test', _PASSWORD)
        session = verify.cookies[policy.SESSION_COOKIE].value
        resp = await self.client.get('/authz?cmd=show&cmd=benchmark',
                                     headers={'Cookie': f'{policy.SESSION_COOKIE}={session}'})
        # show is granted to everyone; benchmark is not granted to guest
        self.assertEqual(await resp.json(), {'show': True, 'benchmark': False})

    async def test_authz_requires_auth(self) -> None:
        self.assertEqual((await self.client.get('/authz?cmd=show')).status, 401)

    async def test_self_service_password_change(self) -> None:
        _c, verify = await self._login(_EMAIL, _PASSWORD, remember=True)
        session = verify.cookies[policy.SESSION_COOKIE].value
        remember = verify.cookies[policy.REMEMBER_COOKIE].value
        new_password = 'a shiny new passphrase'
        token = SrpToken.create(_EMAIL, new_password)
        change = await self.client.post(
            '/password/change', headers={'Cookie': f'{policy.SESSION_COOKIE}={session}'},
            json={'salt': token.salt.hex(), 'verifier': format(token.verifier, 'x')})
        self.assertEqual(change.status, 200)
        _c, with_new = await self._login(_EMAIL, new_password)
        self.assertEqual(with_new.status, 200)                 # new password works
        _c, with_old = await self._login(_EMAIL, _PASSWORD)
        self.assertEqual(with_old.status, 401)                 # old password fails
        stale = await self.client.get('/protected', headers={'Cookie': f'{policy.REMEMBER_COOKIE}={remember}'})
        self.assertEqual(stale.status, 401)                    # remember tokens revoked on change

    async def test_password_change_requires_auth(self) -> None:
        token = SrpToken.create(_EMAIL, 'a password long enough')
        resp = await self.client.post(
            '/password/change', json={'salt': token.salt.hex(), 'verifier': format(token.verifier, 'x')})
        self.assertEqual(resp.status, 401)

    async def test_html_navigation_redirects_when_signed_out(self) -> None:
        resp = await self.client.get('/protected', headers={'Accept': 'text/html'}, allow_redirects=False)
        self.assertEqual(resp.status, 302)
        self.assertIn('/login', resp.headers['Location'])

    async def test_gated_html_page_is_no_store(self) -> None:
        _c, verify = await self._login(_EMAIL, _PASSWORD)
        session = verify.cookies[policy.SESSION_COOKIE].value
        resp = await self.client.get('/protected', headers={
            'Accept': 'text/html', 'Cookie': f'{policy.SESSION_COOKIE}={session}'})
        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.headers.get('Cache-Control'), 'no-store')

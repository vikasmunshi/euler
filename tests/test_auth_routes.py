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

from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase

from solver.web.auth import policy, routes
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
        store.put(_EMAIL, SrpToken.create(_EMAIL, _PASSWORD))
        app = web.Application(middlewares=[auth_middleware])
        setup_auth(app)
        app[routes.USERS] = store               # temp store instead of config.users_file
        app.router.add_get('/protected', self._protected)
        return app

    async def _protected(self, request: web.Request) -> web.Response:
        return web.Response(text='secret')

    async def _login(self, email: str, password: str) -> tuple[SrpClient, web.HTTPException | object]:
        challenge = await self.client.post('/auth/challenge', json={'email': email})
        data = await challenge.json()
        client = SrpClient(email, password)
        m1 = client.process_challenge(bytes.fromhex(data['salt']), int(data['B'], 16))
        verify = await self.client.post(
            '/auth/verify', json={'email': email, 'A': format(client.public, 'x'), 'M1': m1.hex()})
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

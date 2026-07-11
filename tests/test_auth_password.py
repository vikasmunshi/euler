#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The signed-in change-password flow (GET /password + POST /auth/password):
distinct from forgot/reset — the current password is proven over SRP and the
new {salt, verifier} swapped in one atomic exchange. The session that performs
the change stays signed in; every other session and remember token dies."""
from __future__ import annotations

import secrets
import shutil
import tempfile
import unittest
from pathlib import Path

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from solver.web.auth import policy
from solver.web.auth.app import AuthService, build_public_app
from solver.web.auth.config import AuthConfig
from solver.web.auth.srp import SrpClient, compute_verifier

_EMAIL = 'user@example.com'
_OLD = 'Correct-Horse-Battery-1!'
_NEW = 'Staple-Gun-Overdrive-2?'


class ChangePasswordTests(AioHTTPTestCase):
    async def get_application(self):
        state = Path(tempfile.mkdtemp(prefix='euler-auth-test-'))
        self.addCleanup(shutil.rmtree, state, True)
        config = AuthConfig(state_dir=state, socket_path=state / 'auth.sock',
                            admin_socket_path=state / 'admin.sock', socket_group='',
                            admin_socket_group='', admin_token='t',
                            base_url='https://example.test', smtp_relay='127.0.0.1:25',
                            terms_version='test')
        self.service = AuthService(config)
        salt = secrets.token_bytes(16)
        verifier = compute_verifier(salt, _EMAIL, _OLD)
        self.service.users.create(_EMAIL, salt.hex(), f'{verifier:x}', 'test', 'now')
        return build_public_app(self.service)

    def _session(self) -> str:
        return self.service.sessions.create(_EMAIL, 'reader')

    async def _change(self, session: str, current_password: str) -> tuple[int, SrpClient, dict]:
        """Drive the browser's two steps: challenge, then the atomic change POST."""
        cookies = {policy.SESSION_COOKIE: session}
        resp = await self.client.post('/auth/challenge', json={'email': _EMAIL}, cookies=cookies)
        challenge = await resp.json()
        client = SrpClient(_EMAIL, current_password)
        proof = client.process_challenge(bytes.fromhex(challenge['salt']),
                                         int(challenge['B'], 16))
        new_salt = secrets.token_bytes(16)
        new_verifier = compute_verifier(new_salt, _EMAIL, _NEW)
        resp = await self.client.post('/auth/password', cookies=cookies, json={
            'A': f'{client.public:x}', 'M1': proof.hex(),
            'salt': new_salt.hex(), 'verifier': f'{new_verifier:x}',
        })
        body = await resp.json() if resp.status == 200 else {}
        return resp.status, client, body

    @unittest_run_loop
    async def test_page_requires_session(self) -> None:
        resp = await self.client.get('/password', allow_redirects=False)
        self.assertEqual(resp.status, 302)
        self.assertEqual(resp.headers['Location'], '/login')
        resp = await self.client.get('/password',
                                     cookies={policy.SESSION_COOKIE: self._session()})
        self.assertEqual(resp.status, 200)
        body = await resp.text()
        self.assertIn(_EMAIL, body)
        self.assertIn('Current password', body)
        self.assertIn('/assets/password.js', body)
        self.assertIn('<!DOCTYPE', body)                     # the full standalone page

    @unittest_run_loop
    async def test_htmx_gets_a_bare_fragment(self) -> None:
        # The content shell fetches /password (and /terms) for its left pane: a
        # bare fragment (no auth card / no <html>), with the OOB breadcrumb and
        # the external SRP scripts htmx will execute.
        resp = await self.client.get('/password', headers={'HX-Request': 'true'},
                                     cookies={policy.SESSION_COOKIE: self._session()})
        self.assertEqual(resp.status, 200)
        body = await resp.text()
        self.assertNotIn('<!DOCTYPE', body)                  # a fragment…
        self.assertIn('id="password-form"', body)            # …just the form…
        self.assertIn('/assets/srp.js', body)                # …+ the SRP scripts…
        self.assertIn('hx-swap-oob', body)                   # …+ the OOB crumb
        self.assertIn(_EMAIL, body)

        resp = await self.client.get('/terms', headers={'HX-Request': 'true'})
        self.assertEqual(resp.status, 200)
        body = await resp.text()
        self.assertNotIn('<!DOCTYPE', body)
        self.assertIn('invitation-only', body)               # the terms text
        self.assertIn('hx-swap-oob', body)

    @unittest_run_loop
    async def test_endpoint_requires_session(self) -> None:
        resp = await self.client.post('/auth/password', json={})
        self.assertEqual(resp.status, 401)

    @unittest_run_loop
    async def test_change_swaps_credentials_and_keeps_only_this_session(self) -> None:
        mine, other = self._session(), self._session()
        before = self.service.users.get(_EMAIL)
        assert before is not None
        status, client, body = await self._change(mine, _OLD)
        self.assertEqual(status, 200)
        self.assertTrue(client.verify_session(bytes.fromhex(body['M2'])))  # mutual auth
        after = self.service.users.get(_EMAIL)
        assert after is not None
        self.assertNotEqual(after.verifier, before.verifier)               # new credentials
        self.assertIsNotNone(self.service.sessions.get(mine))              # I stay signed in
        self.assertIsNone(self.service.sessions.get(other))                # other devices out
        # …and the new password signs in (full handshake against the new verifier)
        salt_hex, public_hex = self.service.start_challenge(_EMAIL)
        fresh = SrpClient(_EMAIL, _NEW)
        proof = fresh.process_challenge(bytes.fromhex(salt_hex), int(public_hex, 16))
        self.assertIsNotNone(
            self.service.finish_challenge(_EMAIL, f'{fresh.public:x}', proof.hex()))

    @unittest_run_loop
    async def test_wrong_current_password_changes_nothing(self) -> None:
        mine, other = self._session(), self._session()
        before = self.service.users.get(_EMAIL)
        assert before is not None
        status, _client, _body = await self._change(mine, 'Not-The-Password-9#')
        self.assertEqual(status, 401)
        after = self.service.users.get(_EMAIL)
        assert after is not None
        self.assertEqual(after.verifier, before.verifier)                  # untouched
        self.assertIsNotNone(self.service.sessions.get(mine))              # nobody logged out
        self.assertIsNotNone(self.service.sessions.get(other))


if __name__ == '__main__':
    unittest.main()

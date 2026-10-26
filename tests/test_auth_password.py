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

from euler_site.auth import policy
from euler_site.auth.app import AuthService, build_public_app
from euler_site.auth.config import AuthConfig
from euler_site.auth.srp import KDF, KDF_LEGACY, SrpClient, compute_verifier

from tests import silence

silence()   # quiet console + filter aiohttp's request-key warning (isolated-run cleanliness)

_EMAIL = 'user@example.com'
_OLD = 'Correct-Horse-Battery-1!'
_NEW = 'Staple-Gun-Overdrive-2?'


class _AuthCase(AioHTTPTestCase):
    """The public app over a fresh state dir, with one registered account (`_EMAIL`, `_OLD`)."""

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


class ChangePasswordTests(_AuthCase):
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
            'A': f'{client.public:x}', 'M1': proof.hex(), 'id': challenge['id'],
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
        salt_hex, public_hex, cid, _kdf = self.service.start_challenge(_EMAIL)
        fresh = SrpClient(_EMAIL, _NEW)
        proof = fresh.process_challenge(bytes.fromhex(salt_hex), int(public_hex, 16))
        self.assertIsNotNone(
            self.service.finish_challenge(_EMAIL, f'{fresh.public:x}', proof.hex(), cid))

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

    @unittest_run_loop
    async def test_a_handshake_begun_before_a_reset_cannot_finish_after_it(self) -> None:
        """The old password must not open a session once the verifier has been replaced.

        The challenge holds a server built from the verifier of its moment; a reset that
        lands inside the challenge's lifetime replaces the stored verifier, and the
        handshake must then fail even though its proof is right for the old password.
        """
        resp = await self.client.post('/auth/challenge', json={'email': _EMAIL})
        challenge = await resp.json()
        new_salt = secrets.token_bytes(16)                          # the reset completes…
        self.service.users.set_credentials(
            _EMAIL, new_salt.hex(), f'{compute_verifier(new_salt, _EMAIL, _NEW):x}')
        client = SrpClient(_EMAIL, _OLD)                            # …and the old password tries
        proof = client.process_challenge(bytes.fromhex(challenge['salt']), int(challenge['B'], 16))
        resp = await self.client.post('/auth/verify', json={
            'email': _EMAIL, 'A': f'{client.public:x}', 'M1': proof.hex(), 'id': challenge['id'],
            'remember': True})
        self.assertEqual(resp.status, 401)
        self.assertNotIn(policy.SESSION_COOKIE, resp.cookies)
        self.assertNotIn(policy.REMEMBER_COOKIE, resp.cookies)

    def test_a_decoy_salt_survives_a_restart(self) -> None:
        """A real account's salt is stable across restarts, so an unknown address's decoy must
        be too — otherwise comparing the two across a restart tells them apart."""
        before = self.service.start_challenge('nobody@example.test')[0]
        restarted = AuthService(self.service.config)
        self.assertEqual(restarted.start_challenge('nobody@example.test')[0], before)

    @unittest_run_loop
    async def test_the_new_password_still_signs_in_after_a_change(self) -> None:
        status, _client, _body = await self._change(self._session(), _OLD)
        self.assertEqual(status, 200)
        resp = await self.client.post('/auth/challenge', json={'email': _EMAIL})
        challenge = await resp.json()
        client = SrpClient(_EMAIL, _NEW)
        proof = client.process_challenge(bytes.fromhex(challenge['salt']), int(challenge['B'], 16))
        resp = await self.client.post('/auth/verify', json={
            'email': _EMAIL, 'A': f'{client.public:x}', 'M1': proof.hex(), 'id': challenge['id']})
        self.assertEqual(resp.status, 200)

    def _proof(self, challenge: tuple[str, str, str, str], password: str = _OLD) -> tuple[str, str]:
        client = SrpClient(_EMAIL, password)
        proof = client.process_challenge(bytes.fromhex(challenge[0]), int(challenge[1], 16))
        return f'{client.public:x}', proof.hex()

    def test_a_second_handshake_does_not_cancel_the_first(self) -> None:
        """Anyone may start a handshake for an address; that must not end its owner's."""
        mine = self.service.start_challenge(_EMAIL)
        self.service.start_challenge(_EMAIL)                       # someone else's, same address
        self.assertIsNotNone(self.service.finish_challenge(_EMAIL, *self._proof(mine), mine[2]))

    def test_a_handshake_finishes_once_and_only_for_its_own_address(self) -> None:
        challenge = self.service.start_challenge(_EMAIL)
        a, m1 = self._proof(challenge)
        self.assertIsNone(self.service.finish_challenge('other@example.com', a, m1, challenge[2]))
        self.assertIsNone(self.service.finish_challenge(_EMAIL, a, m1, challenge[2]),
                          'a failed attempt spends the id')
        replay = self.service.start_challenge(_EMAIL)
        a, m1 = self._proof(replay)
        self.assertIsNotNone(self.service.finish_challenge(_EMAIL, a, m1, replay[2]))
        self.assertIsNone(self.service.finish_challenge(_EMAIL, a, m1, replay[2]), 'no replay')

    def test_a_decoy_challenge_looks_like_an_upgraded_account(self) -> None:
        """An id, and the current KDF named — the shape a real, upgraded account answers with."""
        _salt, _b, cid, kdf = self.service.start_challenge('nobody@example.test')
        self.assertTrue(cid)
        self.assertEqual(kdf, KDF)


class PasswordHashUpgradeTests(_AuthCase):
    """An account on the legacy password hash moves to Argon2id at its next sign-in — only then,
    only with a valid proof, and keeping its salt (the vault key is derived from it)."""

    def _make_legacy(self) -> str:
        salt = secrets.token_bytes(16)
        self.service.users.set_credentials(
            _EMAIL, salt.hex(), f'{compute_verifier(salt, _EMAIL, _OLD, KDF_LEGACY):x}', kdf=KDF_LEGACY)
        return salt.hex()

    def _sign_in(self, password: str, upgrade: bool) -> bool:
        salt_hex, b_hex, cid, kdf = self.service.start_challenge(_EMAIL)
        client = SrpClient(_EMAIL, password, kdf)
        proof = client.process_challenge(bytes.fromhex(salt_hex), int(b_hex, 16))
        new = f'{compute_verifier(bytes.fromhex(salt_hex), _EMAIL, password, KDF):x}' if upgrade else ''
        return self.service.finish_challenge(_EMAIL, f'{client.public:x}', proof.hex(), cid, new) is not None

    def test_a_legacy_challenge_says_so(self) -> None:
        self._make_legacy()
        self.assertEqual(self.service.start_challenge(_EMAIL)[3], KDF_LEGACY)

    def test_a_sign_in_upgrades_and_keeps_the_salt(self) -> None:
        salt = self._make_legacy()
        self.assertTrue(self._sign_in(_OLD, upgrade=True))
        record = self.service.users.get(_EMAIL)
        assert record is not None
        self.assertEqual((record.kdf, record.salt), (KDF, salt))
        self.assertTrue(self._sign_in(_OLD, upgrade=False), 'the same password, now under Argon2id')

    def test_a_failed_proof_upgrades_nothing(self) -> None:
        self._make_legacy()
        self.assertFalse(self._sign_in('Not-The-Password-9#', upgrade=True))
        record = self.service.users.get(_EMAIL)
        assert record is not None
        self.assertEqual(record.kdf, KDF_LEGACY)

    def test_a_current_account_ignores_an_upgrade(self) -> None:
        before = self.service.users.get(_EMAIL)
        self.assertTrue(self._sign_in(_OLD, upgrade=False))
        salt_hex, b_hex, cid, kdf = self.service.start_challenge(_EMAIL)
        client = SrpClient(_EMAIL, _OLD, kdf)
        proof = client.process_challenge(bytes.fromhex(salt_hex), int(b_hex, 16))
        self.assertIsNotNone(self.service.finish_challenge(_EMAIL, f'{client.public:x}', proof.hex(), cid, 'ab'))
        self.assertEqual(self.service.users.get(_EMAIL), before, 'nothing to upgrade, nothing written')

    @unittest_run_loop
    async def test_a_change_records_its_kdf_and_refuses_an_unknown_one(self) -> None:
        cookies = {policy.SESSION_COOKIE: self._session()}
        for kdf, status in (('argon2id$m=8,t=1,p=1', 400), (KDF, 200)):
            resp = await self.client.post('/auth/challenge', json={'email': _EMAIL}, cookies=cookies)
            challenge = await resp.json()
            client = SrpClient(_EMAIL, _OLD, challenge['kdf'])
            proof = client.process_challenge(bytes.fromhex(challenge['salt']), int(challenge['B'], 16))
            salt = secrets.token_bytes(16)
            resp = await self.client.post('/auth/password', cookies=cookies, json={
                'A': f'{client.public:x}', 'M1': proof.hex(), 'id': challenge['id'], 'kdf': kdf,
                'salt': salt.hex(), 'verifier': f'{compute_verifier(salt, _EMAIL, _NEW, KDF):x}'})
            self.assertEqual(resp.status, status, kdf)
        record = self.service.users.get(_EMAIL)
        assert record is not None
        self.assertEqual(record.kdf, KDF)


if __name__ == '__main__':
    unittest.main()

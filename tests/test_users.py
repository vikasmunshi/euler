#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Unit tests for solver.web.auth.users (the SRP verifier store)."""
from __future__ import annotations

import json
import stat
import tempfile
import unittest
from pathlib import Path

from solver.web.auth import srp
from solver.web.auth.users import UserStore, normalize_email


class NormalizeEmailTests(unittest.TestCase):
    def test_trims_and_lowercases(self) -> None:
        self.assertEqual(normalize_email('  User@Example.COM '), 'user@example.com')


class UserStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name) / 'users.json'
        self.store = UserStore(self.path)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _token(self, email: str = 'a@b.com', pw: str = 'passwordpassword') -> srp.SrpToken:
        return srp.SrpToken.create(email, pw)

    def test_missing_file_reads_as_empty(self) -> None:
        self.assertEqual(self.store.emails(), [])
        self.assertIsNone(self.store.get('nobody@x.com'))
        self.assertFalse(self.store.is_active('nobody@x.com'))

    def test_register_roundtrip_and_active(self) -> None:
        token = self._token()
        record = self.store.register('User@B.com', token)   # normalized on write
        self.assertEqual(record.email, 'user@b.com')
        self.assertTrue(record.registered)
        self.assertFalse(record.disabled)
        self.assertEqual(record.token, token)
        self.assertEqual(record.profile, 'user')             # default profile
        self.assertTrue(self.store.is_active('USER@b.com'))  # lookup normalizes too

    def test_profile_assigned_at_invite_and_preserved_through_register(self) -> None:
        self.store.invite('admin@b.com', 'admin')
        self.assertEqual(self.store.get('admin@b.com').profile, 'admin')  # type: ignore[union-attr]
        registered = self.store.register('admin@b.com', self._token('admin@b.com'),
                                         self.store.get('admin@b.com').profile)  # type: ignore[union-attr]
        self.assertEqual(registered.profile, 'admin')        # survives registration

    def test_token_drives_successful_handshake(self) -> None:
        self.store.register('a@b.com', srp.SrpToken.create('a@b.com', 's3cret-passphrase'))
        record = self.store.get('a@b.com')
        assert record is not None
        self.assertTrue(srp.verify_password('a@b.com', 's3cret-passphrase', record.token))
        self.assertFalse(srp.verify_password('a@b.com', 'wrong', record.token))

    def test_invite_creates_disabled_unregistered(self) -> None:
        record = self.store.invite('New@User.com')
        self.assertEqual(record.email, 'new@user.com')
        self.assertFalse(record.registered)
        self.assertTrue(record.disabled)
        self.assertIsNone(record.salt)
        self.assertIsNone(record.verifier)
        self.assertFalse(self.store.is_active('new@user.com'))  # invited != active
        self.assertEqual(record.profile, 'user')                 # default profile at invite
        with self.assertRaises(ValueError):
            _ = record.token                                     # no verifier yet

    def test_invite_is_noop_when_present(self) -> None:
        first = self.store.invite('a@b.com')
        again = self.store.invite('A@B.com')
        self.assertEqual(again.created, first.created)
        self.store.register('a@b.com', self._token())
        after = self.store.invite('a@b.com')                     # must not wipe a registered user
        self.assertTrue(after.registered)

    def test_register_enables_invited_and_preserves_created(self) -> None:
        invited = self.store.invite('a@b.com')
        registered = self.store.register('a@b.com', self._token())
        self.assertEqual(registered.created, invited.created)
        self.assertTrue(registered.registered)
        self.assertFalse(registered.disabled)                    # registration enables
        self.assertTrue(self.store.is_active('a@b.com'))

    def test_disable_enable_toggles_active(self) -> None:
        self.store.register('a@b.com', self._token())
        self.assertTrue(self.store.set_disabled('a@b.com', True))
        self.assertFalse(self.store.is_active('a@b.com'))
        self.assertTrue(self.store.set_disabled('a@b.com', False))
        self.assertTrue(self.store.is_active('a@b.com'))
        self.assertFalse(self.store.set_disabled('ghost@x.com', True))

    def test_remove(self) -> None:
        self.store.register('a@b.com', self._token())
        self.assertTrue(self.store.remove('A@B.com'))
        self.assertIsNone(self.store.get('a@b.com'))
        self.assertFalse(self.store.remove('a@b.com'))

    def test_emails_and_records_sorted(self) -> None:
        for email in ('c@x.com', 'a@x.com', 'b@x.com'):
            self.store.register(email, self._token(email))
        self.assertEqual(self.store.emails(), ['a@x.com', 'b@x.com', 'c@x.com'])
        self.assertEqual([r.email for r in self.store.records()], ['a@x.com', 'b@x.com', 'c@x.com'])

    def test_file_is_mode_0600_and_valid_json(self) -> None:
        self.store.register('a@b.com', self._token())
        self.assertEqual(stat.S_IMODE(self.path.stat().st_mode), 0o600)
        data = json.loads(self.path.read_text())
        self.assertEqual(data['version'], srp.VERSION)
        self.assertIn('a@b.com', data['users'])

    def test_rejects_corrupt_store(self) -> None:
        self.path.write_text('{"not": "a store"}')
        with self.assertRaises(ValueError):
            self.store.emails()


if __name__ == '__main__':
    unittest.main()

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

    def _token(self, email: str = 'a@b.com', pw: str = 'pw') -> srp.SrpToken:
        return srp.SrpToken.create(email, pw)

    def test_missing_file_reads_as_empty(self) -> None:
        self.assertEqual(self.store.emails(), [])
        self.assertIsNone(self.store.get('nobody@x.com'))
        self.assertFalse(self.store.is_active('nobody@x.com'))

    def test_put_get_roundtrip_and_active(self) -> None:
        token = self._token()
        record = self.store.put('User@B.com', token)
        self.assertEqual(record.email, 'user@b.com')       # normalized
        self.assertEqual(record.token, token)
        self.assertFalse(record.disabled)
        fetched = self.store.get('user@b.com')
        assert fetched is not None
        self.assertEqual(fetched.token, token)
        self.assertTrue(self.store.is_active('USER@b.com'))  # lookup normalizes too

    def test_token_drives_successful_handshake(self) -> None:
        self.store.put('a@b.com', srp.SrpToken.create('a@b.com', 's3cret'))
        record = self.store.get('a@b.com')
        assert record is not None
        self.assertTrue(srp.verify_password('a@b.com', 's3cret', record.token))
        self.assertFalse(srp.verify_password('a@b.com', 'wrong', record.token))

    def test_disable_enable_toggles_active(self) -> None:
        self.store.put('a@b.com', self._token())
        self.assertTrue(self.store.set_disabled('a@b.com', True))
        self.assertFalse(self.store.is_active('a@b.com'))
        self.assertTrue(self.store.set_disabled('a@b.com', False))
        self.assertTrue(self.store.is_active('a@b.com'))
        self.assertFalse(self.store.set_disabled('ghost@x.com', True))

    def test_put_preserves_created_and_disabled_on_replace(self) -> None:
        first = self.store.put('a@b.com', self._token())
        self.store.set_disabled('a@b.com', True)
        replaced = self.store.put('a@b.com', self._token(pw='new'))
        self.assertEqual(replaced.created, first.created)
        self.assertTrue(replaced.disabled)                 # state preserved
        self.assertNotEqual(replaced.verifier, first.verifier)

    def test_remove(self) -> None:
        self.store.put('a@b.com', self._token())
        self.assertTrue(self.store.remove('A@B.com'))
        self.assertIsNone(self.store.get('a@b.com'))
        self.assertFalse(self.store.remove('a@b.com'))

    def test_emails_and_records_sorted(self) -> None:
        for email in ('c@x.com', 'a@x.com', 'b@x.com'):
            self.store.put(email, self._token(email))
        self.assertEqual(self.store.emails(), ['a@x.com', 'b@x.com', 'c@x.com'])
        self.assertEqual([r.email for r in self.store.records()], ['a@x.com', 'b@x.com', 'c@x.com'])

    def test_file_is_mode_0600_and_valid_json(self) -> None:
        self.store.put('a@b.com', self._token())
        mode = stat.S_IMODE(self.path.stat().st_mode)
        self.assertEqual(mode, 0o600)
        data = json.loads(self.path.read_text())
        self.assertEqual(data['version'], srp.VERSION)
        self.assertIn('a@b.com', data['users'])

    def test_rejects_corrupt_store(self) -> None:
        self.path.write_text('{"not": "a store"}')
        with self.assertRaises(ValueError):
            self.store.emails()


if __name__ == '__main__':
    unittest.main()

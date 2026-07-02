#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Unit tests for solver.web.auth.remember (persistent remember-me tokens)."""
from __future__ import annotations

import stat
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from solver.web.auth.remember import RememberStore, load_or_create_secret


class LoadSecretTests(unittest.TestCase):
    def test_create_then_reuse(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / '.session-secret'
            first = load_or_create_secret(path)
            self.assertEqual(len(first), 32)
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            self.assertEqual(load_or_create_secret(path), first)   # reused, not regenerated


class RememberStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name) / 'remember.json'
        self.store = RememberStore(self.path, b'\x00' * 32, ttl_seconds=1000)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_validate_rotates(self) -> None:
        cookie = self.store.issue('a@b.com')
        self.assertIn(':', cookie)
        result = self.store.validate_and_rotate(cookie)
        assert result is not None
        email, rotated = result
        self.assertEqual(email, 'a@b.com')
        self.assertNotEqual(rotated, cookie)                       # validator rotated
        self.assertIsNotNone(self.store.validate_and_rotate(rotated))  # rotated cookie works

    def test_missing_or_malformed(self) -> None:
        self.assertIsNone(self.store.validate_and_rotate(None))
        self.assertIsNone(self.store.validate_and_rotate('no-colon'))
        self.assertIsNone(self.store.validate_and_rotate('unknown:validator'))

    def test_reused_old_validator_revokes_selector(self) -> None:
        cookie = self.store.issue('a@b.com')
        result = self.store.validate_and_rotate(cookie)           # rotate → old validator now stale
        assert result is not None
        _email, rotated = result
        self.assertIsNone(self.store.validate_and_rotate(cookie))  # stale validator → theft → revoke
        self.assertIsNone(self.store.validate_and_rotate(rotated))  # selector gone, rotated cookie dead too

    def test_expiry(self) -> None:
        cookie = self.store.issue('a@b.com')
        with patch('solver.web.auth.remember.time.time', return_value=time.time() + 1001):
            self.assertIsNone(self.store.validate_and_rotate(cookie))

    def test_revoke(self) -> None:
        cookie = self.store.issue('a@b.com')
        self.store.revoke(cookie)
        self.assertIsNone(self.store.validate_and_rotate(cookie))

    def test_revoke_all(self) -> None:
        first = self.store.issue('a@b.com')
        second = self.store.issue('a@b.com')
        other = self.store.issue('other@b.com')
        self.store.revoke_all('a@b.com')
        self.assertIsNone(self.store.validate_and_rotate(first))
        self.assertIsNone(self.store.validate_and_rotate(second))
        self.assertIsNotNone(self.store.validate_and_rotate(other))   # a different user is untouched

    def test_file_mode_and_no_raw_validator(self) -> None:
        cookie = self.store.issue('a@b.com')
        validator = cookie.split(':', 1)[1]
        self.assertEqual(stat.S_IMODE(self.path.stat().st_mode), 0o600)
        self.assertNotIn(validator, self.path.read_text())         # stored HMAC, not the raw validator


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Unit tests for solver.web.auth.otp (OTP generation + the pending-registration store)."""
from __future__ import annotations

import json
import stat
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from solver.web.auth import policy
from solver.web.auth.otp import PendingStore, generate_otp


class GenerateOtpTests(unittest.TestCase):
    def test_length_and_digits(self) -> None:
        otp = generate_otp()
        self.assertEqual(len(otp), policy.OTP_LENGTH)
        self.assertTrue(otp.isdigit())


class PendingStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name) / 'pending.json'
        self.store = PendingStore(self.path)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_unknown_email(self) -> None:
        self.assertFalse(self.store.check('nobody@x.com', '123456', consume=False))

    def test_verify_then_consume(self) -> None:
        self.store.invite('a@b.com', '123456')
        self.assertFalse(self.store.check('a@b.com', '000000', consume=False))  # wrong code
        self.assertTrue(self.store.check('a@b.com', '123456', consume=False))   # right; not consumed
        self.assertTrue(self.store.check('a@b.com', '123456', consume=True))    # right; consumed
        self.assertFalse(self.store.check('a@b.com', '123456', consume=False))  # now gone

    def test_normalizes_email(self) -> None:
        self.store.invite('A@B.com', '111111')
        self.assertTrue(self.store.check('a@b.com', '111111', consume=True))

    def test_attempts_lock_out(self) -> None:
        self.store.invite('a@b.com', '123456')
        for _ in range(policy.OTP_MAX_ATTEMPTS):
            self.assertFalse(self.store.check('a@b.com', '000000', consume=False))
        self.assertFalse(self.store.check('a@b.com', '123456', consume=False))  # locked despite correct code

    def test_expiry_drops_entry(self) -> None:
        self.store.invite('a@b.com', '123456')
        later = time.time() + policy.OTP_TTL_SECONDS + 1
        with patch('solver.web.auth.otp.time.time', return_value=later):
            self.assertFalse(self.store.check('a@b.com', '123456', consume=False))
        self.assertNotIn('a@b.com', json.loads(self.path.read_text())['pending'])

    def test_remove(self) -> None:
        self.store.invite('a@b.com', '123456')
        self.assertTrue(self.store.remove('A@B.com'))
        self.assertFalse(self.store.remove('a@b.com'))

    def test_file_mode_and_otp_not_stored_raw(self) -> None:
        self.store.invite('a@b.com', '123456')
        self.assertEqual(stat.S_IMODE(self.path.stat().st_mode), 0o600)
        entry = json.loads(self.path.read_text())['pending']['a@b.com']
        self.assertIn('salt', entry)
        self.assertEqual(len(entry['hash']), 64)          # sha256 hex, not the raw OTP
        self.assertNotEqual(entry['hash'], '123456')


if __name__ == '__main__':
    unittest.main()

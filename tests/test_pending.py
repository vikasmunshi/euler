#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Unit tests for solver.web.auth.pending (secure-link token generation + store)."""
from __future__ import annotations

import json
import stat
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from solver.web.auth import policy
from solver.web.auth.pending import PendingStore, generate_token


class GenerateTokenTests(unittest.TestCase):
    def test_high_entropy_and_unique(self) -> None:
        tokens = {generate_token() for _ in range(100)}
        self.assertEqual(len(tokens), 100)               # no collisions
        self.assertGreaterEqual(len(next(iter(tokens))), 32)  # URL-safe, plenty long


class PendingStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name) / '.pending.json'
        self.store = PendingStore(self.path)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_unknown_token(self) -> None:
        self.assertIsNone(self.store.resolve('nope'))
        self.assertIsNone(self.store.consume('nope'))
        self.assertIsNone(self.store.resolve(''))

    def test_resolve_then_consume(self) -> None:
        token = self.store.invite('a@b.com', 'register')
        self.assertEqual(self.store.resolve(token), ('a@b.com', 'register'))   # non-consuming
        self.assertEqual(self.store.resolve(token), ('a@b.com', 'register'))   # still there
        self.assertEqual(self.store.consume(token), ('a@b.com', 'register'))   # consumed
        self.assertIsNone(self.store.resolve(token))                           # now gone

    def test_kind_is_carried(self) -> None:
        token = self.store.invite('a@b.com', 'reset')
        self.assertEqual(self.store.resolve(token), ('a@b.com', 'reset'))

    def test_normalizes_email(self) -> None:
        token = self.store.invite('A@B.com')
        self.assertEqual(self.store.consume(token), ('a@b.com', 'register'))

    def test_reinvite_replaces_prior_token(self) -> None:
        first = self.store.invite('a@b.com')
        second = self.store.invite('a@b.com')
        self.assertIsNone(self.store.resolve(first))          # old link is dead
        self.assertEqual(self.store.resolve(second), ('a@b.com', 'register'))

    def test_expiry_drops_entry(self) -> None:
        token = self.store.invite('a@b.com')
        later = time.time() + policy.REGISTRATION_TTL_SECONDS + 1
        with patch('solver.web.auth.pending.time.time', return_value=later):
            self.assertIsNone(self.store.resolve(token))
        self.assertEqual(json.loads(self.path.read_text())['pending'], {})

    def test_remove_email(self) -> None:
        token = self.store.invite('a@b.com')
        self.assertTrue(self.store.remove_email('A@B.com'))
        self.assertFalse(self.store.remove_email('a@b.com'))
        self.assertIsNone(self.store.resolve(token))

    def test_file_mode_and_token_not_stored_raw(self) -> None:
        token = self.store.invite('a@b.com')
        self.assertEqual(stat.S_IMODE(self.path.stat().st_mode), 0o600)
        pending = json.loads(self.path.read_text())['pending']
        self.assertNotIn(token, pending)                      # keyed by hash, not the token
        (digest,) = pending.keys()
        self.assertEqual(len(digest), 64)                     # sha256 hex
        self.assertEqual(pending[digest]['email'], 'a@b.com')


if __name__ == '__main__':
    unittest.main()

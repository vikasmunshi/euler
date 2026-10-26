#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The admin plane's rewrite of authorizations.json keeps the file's group and mode.

The map names every collaborator and is deployed `root:euler-authz 0640`; `users add` /
`users change` rewrite it through a temp file, which must not reset it to world-readable.
"""
from __future__ import annotations

import json
import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from euler_site.auth import admin


class AuthzSaveTests(unittest.TestCase):
    def setUp(self) -> None:
        scratch = Path(tempfile.mkdtemp(prefix='euler-authz-save-'))
        self.addCleanup(lambda: __import__('shutil').rmtree(scratch, True))
        self.path = scratch / 'authorizations.json'
        self.enterContext(mock.patch.object(admin, '_AUTHZ_PATH', str(self.path)))

    def test_a_rewrite_keeps_the_mode(self) -> None:
        self.path.write_text('{}')
        os.chmod(self.path, 0o640)
        admin._authz_save({'ladder': [], 'users': {'a@example.com': 'reader'}})
        self.assertEqual(stat.S_IMODE(self.path.stat().st_mode), 0o640)
        self.assertEqual(json.loads(self.path.read_text())['users'], {'a@example.com': 'reader'})

    def test_a_first_write_is_not_world_readable(self) -> None:
        admin._authz_save({'ladder': [], 'users': {}})
        self.assertEqual(stat.S_IMODE(self.path.stat().st_mode), 0o640)


if __name__ == '__main__':
    unittest.main()

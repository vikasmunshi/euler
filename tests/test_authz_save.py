#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The admin plane's rewrite of authorizations.json keeps the file's group and mode.

The map names every collaborator and is deployed `root:euler-authz 0640`; `users add` /
`users change` rewrite it through a temp file, which must not reset it to world-readable.
Each rewrite also publishes every account's own row beside it, readable by that account alone.
"""
from __future__ import annotations

import grp
import json
import os
import pwd
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

    def test_each_account_gets_its_own_row_and_stale_rows_go(self) -> None:
        """A local login with its own private group gets `profiles/<login>`, group-owned by
        it at 0640; an e-mail with no account yet gets nothing; a row for no one is swept."""
        login = pwd.getpwuid(os.getuid()).pw_name
        try:
            own_group = grp.getgrnam(login).gr_gid == os.getgid()
        except KeyError:
            own_group = False
        if not own_group:
            self.skipTest(f'{login} has no private group of its own')
        profiles = self.path.parent / 'profiles'
        profiles.mkdir()
        (profiles / 'ughost').write_text('{}')
        admin._authz_save({'users': {login: 'contributor', 'nobody-yet@example.com': 'reader'}})
        self.assertEqual(sorted(p.name for p in profiles.iterdir()), [login])
        row = profiles / login
        self.assertEqual(json.loads(row.read_text()), {'users': {login: 'contributor'}})
        self.assertEqual((stat.S_IMODE(row.stat().st_mode), row.stat().st_gid), (0o640, os.getgid()))


if __name__ == '__main__':
    unittest.main()

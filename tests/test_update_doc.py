#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Tests for the commands.csv reconciliation in solver.utils.update_doc (_sync_commands)."""
from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from solver.config import config
from solver.shell.command import registry
from solver.utils.loader import load_commands
from solver.utils.update_doc import _sync_commands


class SyncCommandsTests(unittest.TestCase):
    def setUp(self) -> None:
        self._saved_file = config.commands_file
        self._saved_profile = config.user_profile
        config.user_profile = 'admin'          # the sync only runs as admin
        load_commands('terminal')              # populate the registry (bare unittest doesn't boot the shell)
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.path = Path(self._tmp.name) / 'commands.csv'
        config.commands_file = self.path
        self.addCleanup(self._restore)

    def _restore(self) -> None:
        config.commands_file = self._saved_file
        config.user_profile = self._saved_profile

    def _rows(self) -> dict[str, tuple[str, str, str]]:
        with open(self.path, newline='') as handle:
            return {r[0]: (r[1], r[2], r[3]) for r in csv.reader(handle) if len(r) == 4 and r[0] != 'command'}

    def test_adds_new_drops_removed_and_preserves_edits(self) -> None:
        real = registry.all()[0].name                 # a real command, manually set to admin-only
        self.path.write_text('command,admin,user,guest\n'
                             f'{real},True,,\n'
                             'ghost-command,True,True,True\n')          # not in the registry
        entry = _sync_commands(check=False)
        self.assertIsNotNone(entry)                                     # it changed
        rows = self._rows()

        self.assertNotIn('ghost-command', rows)                        # removed command dropped
        self.assertEqual(rows[real], ('True', '', ''))                 # manual grant preserved verbatim
        names = {c.name for c in registry.all()}
        self.assertEqual(set(rows), names)                             # exactly the live command set
        another = next(c.name for c in registry.all() if c.name != real)
        self.assertEqual(rows[another], ('True', 'True', ''))          # new command → admin + user default

    def test_idempotent_when_in_sync(self) -> None:
        _sync_commands(check=False)                                    # bring the temp file into sync
        self.assertIsNone(_sync_commands(check=False))                 # a second pass is a no-op

    def test_check_mode_reports_without_writing(self) -> None:
        self.path.write_text('command,admin,user,guest\n')            # empty → every command missing
        self.assertIsNotNone(_sync_commands(check=True))              # reports stale
        self.assertEqual(self.path.read_text(), 'command,admin,user,guest\n')  # but wrote nothing

    def test_skipped_for_non_admin_profile(self) -> None:
        self.path.write_text('command,admin,user,guest\n')
        config.user_profile = 'user'
        self.assertIsNone(_sync_commands(check=False))                # never prunes under a lesser profile


if __name__ == '__main__':
    unittest.main()

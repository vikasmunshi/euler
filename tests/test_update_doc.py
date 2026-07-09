#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Tests for the commands.json audit generation in solver.utils.update_doc
(_sync_commands, DD-12) — the generated audit view of each command's
``requires``/``channels``, distinct from the authored ``authorizations.json``."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from solver.auth import Authorizations, Subject
from solver.config import config
from solver.shell.command import registry
from solver.utils import update_doc
from solver.utils.loader import load_commands
from solver.utils.update_doc import _sync_commands

_AUTHZ = Authorizations.load()


def _admin_subject() -> Subject:
    return Subject(user='t', slug='t-000000', channel='terminal', auth_method='test',
                   profile='admin', permissions=_AUTHZ.permissions_for('admin'))


class SyncCommandsTests(unittest.TestCase):
    def setUp(self) -> None:
        self._saved_subject = config.subject
        self._saved_path = update_doc._COMMANDS_JSON
        config.subject = _admin_subject()          # the sync only runs as admin
        load_commands()                            # populate the registry
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.path = Path(self._tmp.name) / 'commands.json'
        update_doc._COMMANDS_JSON = self.path
        self.addCleanup(self._restore)

    def _restore(self) -> None:
        update_doc._COMMANDS_JSON = self._saved_path
        config.subject = self._saved_subject

    def test_generates_audit_of_the_live_registry(self) -> None:
        entry = _sync_commands(check=False)
        self.assertIsNotNone(entry)                                    # wrote the file (was absent)
        audit = json.loads(self.path.read_text())
        self.assertEqual(set(audit), {c.name for c in registry.all()})  # exactly the live set
        sample = registry.all()[0]
        self.assertEqual(audit[sample.name]['requires'], list(sample.requires))
        self.assertEqual(audit[sample.name]['channels'], list(sample.channels))

    def test_idempotent_when_in_sync(self) -> None:
        _sync_commands(check=False)                                    # bring the temp file into sync
        self.assertIsNone(_sync_commands(check=False))                 # a second pass is a no-op

    def test_check_mode_reports_without_writing(self) -> None:
        self.assertIsNotNone(_sync_commands(check=True))              # reports stale (file absent)
        self.assertFalse(self.path.exists())                         # but wrote nothing

    def test_skipped_for_non_admin_profile(self) -> None:
        config.subject = config.subject._replace(profile='contributor')
        self.assertIsNone(_sync_commands(check=False))                # never regenerates under a lesser profile


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The `tool-setup` command: the per-user tool installer, its actions and its confirmation."""
from __future__ import annotations

import unittest
from unittest.mock import patch

from solver.config import config
from solver.shell.dialogue import Abort
from solver.utils import scripts
from tests import silence

silence()


class ToolSetupTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ran: list[str] = []
        self.rc = 0
        self.enterContext(patch.object(scripts, 'run_cmdline', self._record))
        self.script = config.scripts.install_claude

    def _record(self, cmdline: str) -> int:
        self.ran.append(cmdline)
        return self.rc

    def test_install_is_the_default_and_asks_nothing(self) -> None:
        with patch.object(scripts, 'confirm', side_effect=AssertionError('asked')):
            self.assertEqual(scripts.tool_setup('claude'), 0)
        self.assertEqual(self.ran, [f'{self.script} install'])

    def test_reinstall_uninstalls_then_installs(self) -> None:
        with patch.object(scripts, 'confirm', return_value=True):
            self.assertEqual(scripts.tool_setup('claude', 'reinstall'), 0)
        self.assertEqual(self.ran, [f'{self.script} uninstall', f'{self.script} install'])

    def test_uninstall_runs_only_the_uninstall(self) -> None:
        with patch.object(scripts, 'confirm', return_value=True):
            self.assertEqual(scripts.tool_setup('claude', 'uninstall'), 0)
        self.assertEqual(self.ran, [f'{self.script} uninstall'])

    def test_a_failed_uninstall_stops_a_reinstall(self) -> None:
        self.rc = 3
        with patch.object(scripts, 'confirm', return_value=True):
            self.assertEqual(scripts.tool_setup('claude', 'reinstall'), 3)
        self.assertEqual(self.ran, [f'{self.script} uninstall'])

    def test_a_declined_removal_runs_nothing(self) -> None:
        for action in ('uninstall', 'reinstall'):
            with self.subTest(action=action), patch.object(scripts, 'confirm', return_value=False):
                with self.assertRaises(Abort):
                    scripts.tool_setup('claude', action)
        self.assertEqual(self.ran, [])

    def test_the_floor_is_contributor(self) -> None:
        from solver.shell.command import registry
        cmd = registry.resolve('tool-setup')
        assert cmd is not None
        self.assertEqual(cmd.requires, 'contributor')


if __name__ == '__main__':
    unittest.main()

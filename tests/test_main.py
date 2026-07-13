#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Unit tests for solver.main: how ``main`` parses its ``argv`` and dispatches.

The shell itself is stubbed out (``SolverShell`` and ``load_commands`` patched),
so these tests exercise only the argument handling: that ``main`` honours the
``argv`` it is given, falls back to ``sys.argv`` when given ``None``, chooses the
command-block vs. interactive path from the positional ``cmdline``, and derives
the ``--save`` flag correctly. There is no channel flag: the terminal/web channel
comes from the resolved subject (DD-13), never from ``argv``.
"""
from __future__ import annotations

import contextlib
import io
import sys
import unittest
from unittest.mock import patch

from solver.main import main


class MainArgvTests(unittest.TestCase):
    def setUp(self) -> None:
        # Stub the shell so no real command runs; capture how it is constructed
        # and which run-method main calls.
        load_patch = patch('solver.main.load_commands')
        shell_patch = patch('solver.main.SolverShell')
        self.mock_load = load_patch.start()
        self.MockShell = shell_patch.start()
        self.addCleanup(load_patch.stop)
        self.addCleanup(shell_patch.stop)
        self.instance = self.MockShell.return_value
        self.instance.run_command.return_value = 0
        self.instance.run_interactive.return_value = 0

    def test_cmdline_argv_is_honored(self) -> None:
        """A positional block in argv runs as a command block (not sys.argv)."""
        rc = main(['ls 42'])
        self.mock_load.assert_called_once_with()
        self.MockShell.assert_called_once_with(save=False)
        self.instance.run_command.assert_called_once_with(['ls 42'])
        self.instance.run_interactive.assert_not_called()
        self.assertEqual(rc, 0)

    def test_multiple_cmdline_tokens_forwarded_verbatim(self) -> None:
        """Every positional token is forwarded to run_command in order."""
        main(['eval 1', 'benchmark 1'])
        self.instance.run_command.assert_called_once_with(['eval 1', 'benchmark 1'])

    def test_empty_argv_runs_interactive(self) -> None:
        """No positional block → the interactive shell, not a command block."""
        rc = main([])
        self.instance.run_interactive.assert_called_once_with(intro_message='')
        self.instance.run_command.assert_not_called()
        self.assertEqual(rc, 0)

    def test_none_argv_falls_back_to_sys_argv(self) -> None:
        """argv=None parses sys.argv[1:] (argparse's default)."""
        with patch.object(sys, 'argv', ['solver', 'eval 7']):
            main(None)
        self.instance.run_command.assert_called_once_with(['eval 7'])

    def test_save_flag_set_for_interactive(self) -> None:
        """`-s` with no block → an interactive session with save enabled."""
        main(['-s'])
        self.MockShell.assert_called_once_with(save=True)
        self.instance.run_interactive.assert_called_once_with(intro_message='')

    def test_save_flag_ignored_with_cmdline(self) -> None:
        """`-s` alongside a block → save is suppressed (only interactive sessions log)."""
        main(['-s', 'ls 1'])
        self.MockShell.assert_called_once_with(save=False)
        self.instance.run_command.assert_called_once_with(['ls 1'])

    def test_return_code_is_forwarded(self) -> None:
        """main returns the shell's exit status verbatim."""
        self.instance.run_command.return_value = 3
        self.assertEqual(main(['ls 1']), 3)

    def test_no_channel_flag(self) -> None:
        """The channel is not selectable from argv (DD-13): the retired ``--web`` /
        ``--terminal`` flags are usage errors, so no caller can pick its command set —
        it follows from the resolved subject (ticket / checkout-owner uid)."""
        for flag in ('--web', '--terminal'):
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as ctx:
                    main([flag, 'ls 1'])
            self.assertEqual(ctx.exception.code, 2, flag)
        self.MockShell.assert_not_called()

    def test_version_action_reads_from_argv(self) -> None:
        """`--version` in argv triggers argparse's version exit (proving argv is parsed)."""
        with contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as ctx:
                main(['--version'])
        self.assertEqual(ctx.exception.code, 0)
        self.instance.run_command.assert_not_called()
        self.instance.run_interactive.assert_not_called()


if __name__ == '__main__':  # pragma: no cover
    unittest.main()

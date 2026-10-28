#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The start-up banner's status line (:func:`solver.shell.login.status_line`) and its layout.

Every probe is stubbed — no vault, key file or git is read — and the point throughout is that
each state is *reported*, never raised: a broken key file must not stop the shell starting.
"""
from __future__ import annotations

import unittest
from unittest.mock import patch

from solver.config import config
from solver.crypto import vault
from solver.shell import SolverShell, login
from tests import silence

silence()


class StatusLineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.enterContext(patch.object(vault, 'vault_exists', return_value=True))
        self.enterContext(patch.object(vault, 'session_vault_key', return_value=b'k'))
        self.enterContext(patch.object(login, 'read_master_key', return_value=b'm'))
        self.enterContext(patch('solver.utils.version.git_describe', return_value='v1.2.3-4-gabc'))

    def test_segments_name_the_subject_the_keys_and_the_clone(self) -> None:
        who, keys, git = login.status_line()
        self.assertIn(config.subject.user, who)
        self.assertIn(config.subject.profile, who)
        self.assertIn(config.subject.channel, who)
        self.assertIn('vault unlocked', keys)
        self.assertIn('master key [success]✓', keys)
        self.assertEqual(git, 'git v1.2.3-4-gabc')

    def test_no_git_drops_the_segment(self) -> None:
        with patch('solver.utils.version.git_describe', return_value=None):
            self.assertEqual(len(login.status_line()), 2)

    def test_no_vault(self) -> None:
        with patch.object(vault, 'vault_exists', return_value=False):
            self.assertIn('no vault', login._vault_state())

    def test_locked_vault_does_not_probe_the_master_key(self) -> None:
        with patch.object(vault, 'session_vault_key', return_value=None), \
                patch.object(login, 'read_master_key', side_effect=AssertionError('probed')):
            self.assertIn('vault locked', login._vault_state())
            self.assertIn('locked', login._master_key_state())

    def test_master_key_failures_are_words_not_exceptions(self) -> None:
        cases = {KeyError('x'): 'not authorized', ValueError('x'): 'invalid', RuntimeError('x'): 'invalid'}
        for exc, word in cases.items():
            with self.subTest(exc=exc), patch.object(login, 'read_master_key', side_effect=exc):
                self.assertIn(word, login._master_key_state())

    def test_missing_files(self) -> None:
        with patch.object(login, 'read_master_key', side_effect=FileNotFoundError):
            with patch.object(type(config.private_key_file), 'exists', return_value=False):
                self.assertIn('no identity', login._master_key_state())
            with patch.object(type(config.private_key_file), 'exists', return_value=True):
                self.assertIn('not issued', login._master_key_state())


class StatusLayoutTests(unittest.TestCase):
    def _lines(self, width: int) -> list[str]:
        shell = SolverShell(save=False)
        with patch.object(type(shell.console), 'width', new=width):
            return [line.plain for line in shell._status_lines(('a' * 20, 'b' * 20, 'c' * 20))]

    def test_wide_terminal_keeps_one_line(self) -> None:
        self.assertEqual(self._lines(120), [f'  {"a" * 20}   {"b" * 20}   {"c" * 20}'])

    def test_narrow_terminal_breaks_between_segments(self) -> None:
        self.assertEqual(self._lines(55), [f'  {"a" * 20}   {"b" * 20}', f'  {"c" * 20}'])


if __name__ == '__main__':
    unittest.main()

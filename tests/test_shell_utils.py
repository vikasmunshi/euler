#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The block-pacing commands — `pause`, `sleep`, `random` — and the unregistered-answer notice format."""
from __future__ import annotations

import unittest
from unittest.mock import patch

from solver.config import ExitCodes
from solver.core.notices import UNREGISTERED_LINE, unregistered_problems
from solver.utils import shell_utils
from tests import silence

silence()


class PauseTests(unittest.TestCase):
    def test_the_prompt_is_what_the_dialogue_shows(self) -> None:
        with patch('solver.utils.shell_utils.dialogue.pause') as shown:
            self.assertEqual(shell_utils.pause('registered?'), ExitCodes.EXIT_OK)
        shown.assert_called_once_with('registered?')

    def test_without_a_prompt_it_says_paused(self) -> None:
        with patch('solver.utils.shell_utils.dialogue.pause') as shown:
            shell_utils.pause()
        shown.assert_called_once_with('paused')


class SleepTests(unittest.TestCase):
    def test_it_waits_the_seconds_given(self) -> None:
        with patch('solver.utils.shell_utils.time.sleep') as slept:
            self.assertEqual(shell_utils.sleep(42), ExitCodes.EXIT_OK)
        slept.assert_called_once_with(42)

    def test_a_negative_time_is_a_usage_error_and_no_wait(self) -> None:
        with patch('solver.utils.shell_utils.time.sleep') as slept:
            self.assertEqual(shell_utils.sleep(-1), ExitCodes.EXIT_USAGE)
        slept.assert_not_called()


class RandomTests(unittest.TestCase):
    def test_the_defaults_are_one_to_a_hundred(self) -> None:
        drawn = {shell_utils.random() for _ in range(2000)}
        self.assertEqual((min(drawn), max(drawn)), (1, 100))

    def test_both_bounds_are_included(self) -> None:
        drawn = {shell_utils.random(3, 1) for _ in range(200)}
        self.assertEqual(drawn, {1, 2, 3})

    def test_max_comes_first_as_in_wait_equals_random_3600_1800(self) -> None:
        for _ in range(200):
            self.assertTrue(1800 <= shell_utils.random(3600, 1800) <= 3600)

    def test_equal_bounds_give_that_number(self) -> None:
        self.assertEqual(shell_utils.random(5, 5), 5)

    def test_min_above_max_is_a_usage_error(self) -> None:
        self.assertEqual(shell_utils.random(1, 9), ExitCodes.EXIT_USAGE)


class EchoTests(unittest.TestCase):
    """`execute(echo=False)`: the block runs the same, without the statement trail."""

    def _run(self, echo: bool) -> tuple[int, list[str]]:
        from solver.shell.interpreter import execute
        from solver.shell.lexer import lex
        from solver.shell.parser import parse
        ran: list[str] = []

        def command(name: str, args: list[str]) -> int:
            ran.append(name)
            return 0

        loop, statements = parse(lex('loop [1, 2]: { echo_test {loop}; left = {loop} }'))
        with patch('solver.shell.interpreter.console.print') as printed:
            rc = execute(loop, statements, command=command, echo=echo)
        return rc, [str(call.args[0]) for call in printed.call_args_list] + ran

    def test_echo_on_trails_every_statement(self) -> None:
        rc, out = self._run(echo=True)
        self.assertEqual(rc, 0)
        self.assertIn('echo_test 1 → 0', out)
        self.assertIn('left = 2', out)

    def test_echo_off_runs_the_same_statements_silently(self) -> None:
        rc, out = self._run(echo=False)
        self.assertEqual(rc, 0)
        self.assertEqual(out, ['echo_test', 'echo_test'])

    def test_echo_comes_back_on_afterwards(self) -> None:
        from solver.shell import interpreter
        self._run(echo=False)
        self.assertTrue(interpreter._echo)


class UnregisteredLineTests(unittest.TestCase):
    def test_the_numbers_round_trip_through_the_body(self) -> None:
        body = ('These problems are recorded as solved:\n\n'
                + ''.join(f'    {UNREGISTERED_LINE.format(number=n)}\n' for n in (341, 7, 1006))
                + '\nSubmit each answer on https://projecteuler.net.\n')
        self.assertEqual(unregistered_problems(body), [341, 7, 1006])

    def test_prose_mentioning_a_problem_is_not_a_line(self) -> None:
        self.assertEqual(unregistered_problems('see answer for problem 12 not registered yet'), [])


if __name__ == '__main__':
    unittest.main()

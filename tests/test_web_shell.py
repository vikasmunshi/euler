#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Unit tests for the web shell (solver.web.shell): its overlay table against the real registry,
the OSC nudges it sends, and the `show` / `edit` bodies that replace the solver shell's own."""
from __future__ import annotations

import contextlib
import io
import unittest
from typing import Iterator
from unittest.mock import patch

from solver.config import ExitCodes, config
from solver.core import viewer as core_viewer
from solver.core.problems import Problem
from solver.shell.command import registry
from solver.shell.extension import check_overlays
from solver.utils.loader import load_commands
from solver.web.shell import extension, osc, viewer
from tests import silence

silence()


@contextlib.contextmanager
def channel(name: str) -> Iterator[io.StringIO]:
    """Run as the current subject on channel *name*, capturing stdout (where OSC is written)."""
    saved = config.subject
    config.subject = saved._replace(channel=name)
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            yield out
    finally:
        config.subject = saved


def _sequences(text: str) -> list[list[str]]:
    """The OSC 5379 payloads in *text*, each split into its fields."""
    return [chunk.split('\x07', 1)[0].split(';') for chunk in text.split('\x1b]5379;')[1:]]


class OverlayTableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        load_commands()                 # this process is the owner → admin: nothing is withheld

    def test_the_table_fits_the_registry(self) -> None:
        check_overlays(extension())

    def test_every_overlay_names_a_registered_command(self) -> None:
        """Withheld commands are skipped at startup; under the owner none may be, or a typo hides."""
        missing = [o.command for o in extension().overlays if registry.resolve(o.command) is None]
        self.assertEqual(missing, [])


class NudgeTests(unittest.TestCase):
    def test_each_event_sends_its_payload(self) -> None:
        for event in osc.EVENTS:
            with self.subTest(event=event), channel('web') as out:
                osc.nudge(event)
            [fields] = _sequences(out.getvalue())
            self.assertEqual(fields[0], event)
            self.assertTrue(fields[1].isdigit(), 'the token')

    def test_a_terminal_hears_nothing(self) -> None:
        with channel('terminal') as out:
            osc.nudge('git')
        self.assertEqual(out.getvalue(), '')


class ViewerTests(unittest.TestCase):
    problem = Problem.from_number(1)

    def test_show_opens_the_problem_in_the_pane(self) -> None:
        with channel('web') as out:
            self.assertEqual(viewer.show(self.problem), ExitCodes.EXIT_OK)
        [fields] = _sequences(out.getvalue())
        self.assertEqual(fields[:2], ['open', '0001'])

    def test_show_a_path_navigates_the_pane(self) -> None:
        with channel('web') as out:
            self.assertEqual(viewer.show(self.problem, 'topics/'), ExitCodes.EXIT_OK)
        [fields] = _sequences(out.getvalue())
        self.assertEqual((fields[0], fields[2]), ('nav', 'topics/'))

    def test_show_refuses_a_path_outside_the_pane_routes(self) -> None:
        with channel('web') as out:
            self.assertEqual(viewer.show(self.problem, 'terminal/'), ExitCodes.EXIT_ERROR)
        self.assertEqual(_sequences(out.getvalue()), [])

    def test_edit_opens_an_existing_file(self) -> None:
        files = core_viewer._files_of(self.problem)
        self.assertTrue(files, 'problem 1 has files')
        with channel('web') as out:
            self.assertEqual(viewer.edit(self.problem, files[0]), ExitCodes.EXIT_OK)
        [fields] = _sequences(out.getvalue())
        self.assertEqual((fields[0], fields[1], fields[3]), ('edit', '0001', files[0]))

    def test_edit_refuses_a_missing_or_escaping_file(self) -> None:
        for filename in ('no-such-file.py', '../p0002/p0002_s0.py'):
            with self.subTest(filename=filename), channel('web') as out:
                self.assertEqual(viewer.edit(self.problem, filename), ExitCodes.EXIT_ERROR)
            self.assertEqual(_sequences(out.getvalue()), [])

    def test_the_solver_shell_never_emits(self) -> None:
        """Without the web shell, `show` opens a browser tab whatever the channel — no OSC."""
        with channel('web') as out, patch.object(core_viewer, '_browser_is_available', return_value=False):
            self.assertEqual(core_viewer.show(self.problem), ExitCodes.EXIT_ERROR)
        self.assertEqual(_sequences(out.getvalue()), [])


if __name__ == '__main__':
    unittest.main()

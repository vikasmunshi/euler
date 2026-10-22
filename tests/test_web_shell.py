#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Unit tests for the web shell (solver.web.shell): its overlay table against the real registry,
the OSC nudges it sends, and the `show` / `edit` bodies that replace the solver shell's own."""
from __future__ import annotations

import contextlib
import importlib
import io
import os
import sys
import unittest
from typing import Iterator
from unittest.mock import patch

from rich.console import Console

from solver.auth import Subject
from solver.auth.identity import system_slug
from solver.config import ExitCodes, config
from solver.core import viewer as core_viewer
from solver.core.problems import Problem
from solver.shell.command import registry
from solver.shell.extension import check_overlays
from solver.utils.loader import load_commands
from solver.web.shell import extension, host_extension, identity, osc, sync_at_start, viewer
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
        for module in extension().modules:
            importlib.import_module(module)

    def test_the_table_fits_the_registry(self) -> None:
        check_overlays(extension())

    def test_the_host_table_fits_the_registry(self) -> None:
        check_overlays(host_extension())

    def test_both_bring_the_hosts_commands_and_the_spool(self) -> None:
        for ext in (extension(), host_extension()):
            self.assertIn('solver.web.shell.keys', ext.modules)
            self.assertIsNotNone(ext.notices)
        self.assertIn('header', extension().notices.key_hint())          # type: ignore[union-attr]
        self.assertIn('msg act', host_extension().notices.key_hint())    # type: ignore[union-attr]

    def test_the_host_terminal_is_the_os_login_and_may_prompt(self) -> None:
        ext = host_extension()
        self.assertIsNone(ext.identity)
        self.assertTrue(ext.prompt_vault)
        self.assertIsNone(ext.notify)

    def test_every_overlay_names_a_registered_command(self) -> None:
        """Withheld commands are skipped at startup; under the owner none may be, or a typo hides."""
        missing = [o.command for o in extension().overlays if registry.resolve(o.command) is None]
        self.assertEqual(missing, [])


class IdentityTests(unittest.TestCase):
    """The web shell runs as its ticket's user, or not at all."""

    def subject(self, redeemed: tuple[str, str] | BaseException, **env: str) -> Subject:
        with patch.dict(os.environ, env), patch.object(identity, '_redeem', side_effect=[redeemed]):
            for name in (identity.TICKET_ENV, identity.SLUG_PIN_ENV):
                if name not in env:
                    os.environ.pop(name, None)
            subject = identity.ticket_subject()
            self.assertNotIn(identity.TICKET_ENV, os.environ, 'the spent ticket is scrubbed')
            return subject

    def test_a_ticket_makes_a_web_subject_with_its_rung(self) -> None:
        """Not capped: an admin account keeps admin over the web, contained by its own uid + SRP."""
        subj = self.subject(('boss@y.z', 'admin'), SOLVER_TICKET='t', EULER_USER_SLUG=system_slug('boss@y.z'))
        self.assertEqual((subj.user, subj.slug, subj.channel, subj.auth_method, subj.profile),
                         ('boss@y.z', system_slug('boss@y.z'), 'web', 'shell-ticket', 'admin'))

    def test_no_ticket_refuses(self) -> None:
        with self.assertRaises(SystemExit):
            self.subject(('x@y.z', 'reader'))

    def test_a_rejected_ticket_refuses(self) -> None:
        with self.assertRaises(SystemExit):
            self.subject(SystemExit('rejected'), SOLVER_TICKET='bad')

    def test_a_ticket_for_another_instance_refuses(self) -> None:
        """The forking instance *is* the user's uid: a ticket for someone else is misrouting."""
        with self.assertRaises(SystemExit):
            self.subject(('x@y.z', 'maintainer'), SOLVER_TICKET='t', EULER_USER_SLUG='u000000')

    def test_the_extension_brings_identity_and_never_prompts(self) -> None:
        ext = extension()
        self.assertIs(ext.identity, identity.ticket_subject)
        self.assertFalse(ext.prompt_vault)


class StartTests(unittest.TestCase):
    def run_start(self, rc: int) -> tuple[list[str], str]:
        ran: list[str] = []
        out = io.StringIO()

        def dispatch(block: str) -> int:
            ran.append(block)
            return rc

        with patch('solver.core.git.key_waiting_hint', return_value=''), \
             patch.object(sys.modules['solver.web.shell'], 'console', Console(file=out)):
            sync_at_start(dispatch)
        return ran, out.getvalue()

    def test_a_good_sync_is_silent(self) -> None:
        self.assertEqual(self.run_start(0), (['git-sync'], ''))

    def test_a_failed_sync_says_so(self) -> None:
        ran, out = self.run_start(1)
        self.assertEqual(ran, ['git-sync'])
        self.assertIn('could not sync', out)


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

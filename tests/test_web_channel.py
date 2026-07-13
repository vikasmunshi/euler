#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The per-rung web-shell command set (Phase 6 step 2, DD-11/DD-13).

The web terminal is the **full** solver shell; what a rung may run is decided by
the DD-12 decorator (``requires`` ⊆ the subject's permissions, and the command's
``channels``) — not by a curated list. This suite is the snapshot of that
decision: it loads every command module (so the registry holds the whole
catalogue, this process being the checkout owner → ``admin``/terminal) and then
asks, for each web rung, which commands *would* register.

The invariants it pins (DD-13):

- ``reader`` gets a terminal, but a **read-only** one — no ``eval``/``benchmark``
  (``solutions:execute``), no ``edit``/``new`` (``solutions:write``).
- **no** web rung — not even ``maintainer`` — gets the shell escape (``!``,
  ``shell:execute``, admin-only), the infra commands (``git-*``/``key-*``), or
  the mutating ``users`` verbs.
- ``show``/``edit`` are back on the web channel (their OSC bridge drives the app
  shell's left pane, Phase 6 step 2).
"""
from __future__ import annotations

import unittest

from solver.auth import Authorizations, Subject
from solver.shell.command import effective_requires, registry
from solver.utils.loader import load_commands

_AUTHZ = Authorizations.load()          # the bundled ladder
_WEB_RUNGS = ('reader', 'contributor', 'maintainer')


def _visible(profile: str, channel: str = 'web') -> set[str]:
    """The commands that would register for *profile* on *channel* (DD-12)."""
    subject = Subject(user='t', slug='t-000000', channel=channel, auth_method='test',
                      profile=profile, permissions=_AUTHZ.permissions_for(profile))
    return {cmd.name for cmd in registry.all()
            if channel in cmd.channels
            and subject.has_all(effective_requires(cmd.requires))}


class WebChannelCommandSetTest(unittest.TestCase):
    """The registry is loaded once; every assertion is a pure metadata query."""

    web: dict[str, set[str]]
    admin_terminal: set[str]

    @classmethod
    def setUpClass(cls) -> None:
        load_commands()                 # this process is the owner → admin/terminal
        cls.web = {rung: _visible(rung) for rung in _WEB_RUNGS}
        cls.admin_terminal = _visible('admin', channel='terminal')

    def test_the_ladder_is_monotonic(self) -> None:
        """Each rung sees everything the rung below it does, and more."""
        self.assertLess(self.web['reader'], self.web['contributor'])
        self.assertLess(self.web['contributor'], self.web['maintainer'])

    def test_reader_terminal_is_read_only(self) -> None:
        """A reader attaches (solver:execute) but runs no user code (DD-13/AR-1)."""
        reader = self.web['reader']
        self.assertLessEqual({'ls', 'show', 'echo', 'problems', 'results'}, reader)
        for denied in ('evaluate', 'benchmark', 'edit', 'new'):
            self.assertNotIn(denied, reader, f'{denied} must not reach a reader shell')

    def test_contributor_adds_edit_and_execute(self) -> None:
        contributor = self.web['contributor']
        self.assertLessEqual({'evaluate', 'benchmark', 'edit', 'new', 'show'}, contributor)

    def test_maintainer_adds_the_ai_commands(self) -> None:
        self.assertLessEqual({'claude-api', 'claude-skill'}, self.web['maintainer'])
        self.assertNotIn('claude-api', self.web['contributor'])

    def test_no_web_rung_has_a_shell_escape(self) -> None:
        """`!` is shell:execute — admin-only, and admin is never web (DD-11)."""
        for rung in _WEB_RUNGS:
            self.assertNotIn('!', self.web[rung], f'{rung} must not have raw bash')
        self.assertIn('!', self.admin_terminal)      # …but the local admin does

    def test_no_web_rung_has_infra_or_user_mutation(self) -> None:
        """infra:execute (git-*/key-*/manage-config/update-*) and users:write are
        local-admin only: no web account administers the host or the roster."""
        infra = {cmd.name for cmd in registry.all()
                 if 'infra:execute' in effective_requires(cmd.requires)}
        self.assertTrue(infra, 'expected some infra commands in the catalogue')
        for rung in _WEB_RUNGS:
            self.assertFalse(infra & self.web[rung],
                             f'{rung} must not see infra commands: {sorted(infra & self.web[rung])}')

    def test_show_and_edit_are_on_the_web_channel(self) -> None:
        """Step 2: the OSC 5379 bridge drives the app shell's left pane, so the
        viewer commands are no longer terminal-only."""
        for name in ('show', 'edit'):
            cmd = registry.resolve(name)
            assert cmd is not None
            self.assertIn('web', cmd.channels, f'{name} must register in a web shell')

    def test_terminal_only_commands_stay_off_the_web(self) -> None:
        """A command declaring channels=('terminal',) never registers in a web shell,
        whatever the profile — the channel axis is orthogonal to permissions (DD-12)."""
        terminal_only = {cmd.name for cmd in registry.all() if cmd.channels == ('terminal',)}
        for rung in _WEB_RUNGS:
            self.assertFalse(terminal_only & self.web[rung])


if __name__ == '__main__':
    unittest.main()

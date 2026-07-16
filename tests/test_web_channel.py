#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The per-rung web-shell command set.

The web terminal is the **full** solver shell; what a rung may run is decided **solely** by
the decorator's ``requires`` floor against the subject's profile — not by a curated list,
and not by any channel axis. This suite is the snapshot of that decision: it loads every
command module (so the registry holds the whole catalogue, this process being the checkout
owner → ``admin``/terminal) and then asks, for each rung, which commands *would* register.

The invariants it pins:

- ``reader`` gets a terminal, but a **read-only** one — no ``evaluate``/``benchmark``, no
  ``edit``/``new``, so a fresh invitee triggers no host execution of user code.
- ``reader`` never gets the shell escape (``!``). Above it, ``!`` simply **tracks the
  policy**: the test reads the floor off the registry and asserts a rung sees ``!`` iff its
  profile satisfies that floor, so it holds wherever the operator sets it rather than
  hardcoding a rung.
- the admin-floored commands (``git-merge``/``key-*``/``manage-config``/``update-*`` and
  the roster mutations) reach **no** web rung — guarded by the ladder floor alone, the
  channel gate having been the redundant backstop that is now gone.
"""
from __future__ import annotations

import unittest

from solver.auth import Subject
from solver.shell.command import registry
from solver.utils.loader import load_commands

_WEB_RUNGS = ('reader', 'contributor', 'maintainer')
#: The tier where a shell escape is a hard no, whatever the policy: a fresh invitee
#: (``reader``) runs no user code at all. ``contributor``+ gets bash by the operator's
#: decision — in the per-user model the shell is the collaborator's OWN uid sandbox,
#: so raw bash grants nothing that `evaluate` (arbitrary Python) did not already.
_NO_ESCAPE_RUNGS = ('reader',)


def _visible(profile: str, channel: str = 'web') -> set[str]:
    """The commands that would register for *profile*. The channel is informational only —
    it does not affect what registers — so visibility is a pure floor query."""
    subject = Subject(user='t', slug='t-000000', channel=channel, auth_method='test',
                      profile=profile)
    return {cmd.name for cmd in registry.all() if subject.has(cmd.requires)}


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
        """Each rung sees everything the rung below it does. contributor and
        maintainer currently expose the same command set (maintainer keeps its
        extra WEB surface — the delete routes); admin adds the infra commands."""
        self.assertLess(self.web['reader'], self.web['contributor'])
        self.assertLessEqual(self.web['contributor'], self.web['maintainer'])
        self.assertLess(self.web['maintainer'], self.admin_terminal)

    def test_reader_terminal_is_read_only(self) -> None:
        """A reader attaches (the reader floor) but runs no user code."""
        reader = self.web['reader']
        self.assertLessEqual({'ls', 'show', 'echo', 'problems', 'results'}, reader)
        for denied in ('evaluate', 'benchmark', 'edit', 'new'):
            self.assertNotIn(denied, reader, f'{denied} must not reach a reader shell')

    def test_contributor_adds_edit_and_execute(self) -> None:
        contributor = self.web['contributor']
        self.assertLessEqual({'evaluate', 'benchmark', 'edit', 'new', 'show'}, contributor)

    def test_contributor_adds_the_ai_commands(self) -> None:
        """AI at contributor (the users-bring-their-own-key model: the spend is
        theirs); a reader still has none."""
        self.assertLessEqual({'claude-api', 'claude-solve'}, self.web['contributor'])
        self.assertNotIn('claude-api', self.web['reader'])

    def test_reader_and_contributor_have_no_shell_escape(self) -> None:
        """A reader never gets raw bash, whatever the policy says; the rungs above
        track the declared floor (see the test below)."""
        for rung in _NO_ESCAPE_RUNGS:
            self.assertNotIn('!', self.web[rung], f'{rung} must not have raw bash')
        self.assertIn('!', self.web['contributor'])  # the operator's chosen floor
        self.assertIn('!', self.admin_terminal)      # …the local admin always does

    def test_shell_escape_tracks_the_policy_grant(self) -> None:
        """A rung sees `!` **iff** its profile satisfies the floor `!` declares — the
        decorator faithfully implements the policy rather than a hardcoded rung. The
        floor is read off the registry here, so wherever the operator sets it this
        passes; a decorator that leaked `!` to a profile below the floor fails."""
        bash = registry.resolve('!')
        assert bash is not None
        floor = bash.requires
        for rung in _WEB_RUNGS:
            at_floor = Subject(user='t', slug='t', channel='web', auth_method='test',
                               profile=rung).has(floor)
            self.assertEqual(at_floor, '!' in self.web[rung],
                             f'{rung}: `!` visible={"!" in self.web[rung]} '
                             f'but floor {floor} satisfied={at_floor}')

    def test_no_web_rung_has_infra_or_user_mutation(self) -> None:
        """The admin-floored commands (git-merge/key-*/manage-config/update-*) and the
        roster mutations: no web account administers the host or the roster."""
        infra = {cmd.name for cmd in registry.all() if cmd.requires == 'admin'}
        self.assertTrue(infra, 'expected some infra commands in the catalogue')
        for rung in _WEB_RUNGS:
            self.assertFalse(infra & self.web[rung],
                             f'{rung} must not see infra commands: {sorted(infra & self.web[rung])}')

    def test_show_and_edit_are_available_to_the_right_rungs(self) -> None:
        """The OSC 5379 bridge drives the app shell's left pane over web, so the viewer commands
        run there gated only by their floors: show reaches a reader, edit a contributor
        and not a reader."""
        self.assertIn('show', self.web['reader'])
        self.assertIn('edit', self.web['contributor'])
        self.assertNotIn('edit', self.web['reader'])

    def test_formerly_terminal_only_commands_are_now_profile_gated(self) -> None:
        """The commands that were ``channels=('terminal',)`` are gated purely by
        ``requires`` now. The infra ones (``update-models``/``update-docs``, admin-floored)
        reach no web rung; ``users`` does register for members at the reader floor, but its
        listing is self-scoped in the command, so it discloses no roster."""
        for infra_cmd in ('update-models', 'update-docs'):
            for rung in _WEB_RUNGS:
                self.assertNotIn(infra_cmd, self.web[rung], f'{infra_cmd} must not reach {rung}')
        self.assertIn('users', self.web['reader'])          # visible at the reader floor, but self-scoped


if __name__ == '__main__':
    unittest.main()

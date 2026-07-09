#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Unit tests for the decorator authorization layer (solver.shell.command, DD-12):
the fail-closed ``requires`` default, ``is_permitted``, and decorator gating against
the resolved :class:`~solver.auth.Subject`."""
from __future__ import annotations

import contextlib
import unittest
from typing import Iterator

from solver.auth import Authorizations, Subject
from solver.config import config
from solver.shell.command import Context, command, effective_requires, is_permitted, registry

_AUTHZ = Authorizations.load()  # built-in default ladder


def _subject(profile: str, channel: str = 'terminal') -> Subject:
    return Subject(user='t', slug='t-000000', channel=channel, auth_method='test',
                   profile=profile, permissions=_AUTHZ.permissions_for(profile))


@contextlib.contextmanager
def as_subject(profile: str, channel: str = 'terminal') -> Iterator[None]:
    """Temporarily run under a subject of *profile*/*channel* (the check reads config.subject)."""
    saved = config.subject
    config.subject = _subject(profile, channel)
    try:
        yield
    finally:
        config.subject = saved


class RequiresTests(unittest.TestCase):
    def test_empty_requires_is_failclosed_to_admin(self) -> None:
        self.assertEqual(effective_requires(()), ('infra:execute',))
        self.assertEqual(effective_requires(('solutions:read',)), ('solutions:read',))

    def test_is_permitted_checks_permission(self) -> None:
        with as_subject('reader'):
            self.assertTrue(is_permitted(('solutions:read',), ('terminal', 'web')))
            self.assertFalse(is_permitted(('solutions:write',), ('terminal', 'web')))
            self.assertFalse(is_permitted((), ('terminal', 'web')))     # fail-closed → admin-only
        with as_subject('contributor'):
            self.assertTrue(is_permitted(('solutions:write',), ('terminal', 'web')))
        with as_subject('admin'):
            self.assertTrue(is_permitted((), ('terminal', 'web')))      # admin has infra:execute

    def test_is_permitted_checks_channel(self) -> None:
        with as_subject('reader', channel='web'):
            self.assertTrue(is_permitted(('solutions:read',), ('terminal', 'web')))
            self.assertFalse(is_permitted(('solutions:read',), ('terminal',)))   # web excluded


class DecoratorEnforcementTests(unittest.TestCase):
    def tearDown(self) -> None:
        for name in ('zz-test-reader', 'zz-test-admin', 'zz-test-web-only'):
            registry.unregister(name)

    def test_unauthorized_command_is_not_registered(self) -> None:
        with as_subject('reader'):
            @command(name='zz-test-admin')                # no requires → admin-only → skipped for reader
            def _f(ctx: Context) -> int:
                return 0
        self.assertIsNone(registry.resolve('zz-test-admin'))    # invisible to help/dispatch
        self.assertEqual(_f(Context()), 0)                      # still a working callable

    def test_authorized_command_is_registered_with_requires(self) -> None:
        with as_subject('reader'):
            @command(name='zz-test-reader', requires=('solutions:read',))
            def _f(ctx: Context) -> int:
                return 0
        cmd = registry.resolve('zz-test-reader')
        self.assertIsNotNone(cmd)
        assert cmd is not None
        self.assertEqual(cmd.requires, ('solutions:read',))

    def test_channel_gating_hides_wrong_channel(self) -> None:
        with as_subject('admin', channel='web'):
            @command(name='zz-test-web-only', requires=('infra:execute',), channels=('terminal',))
            def _f(ctx: Context) -> int:
                return 0
        self.assertIsNone(registry.resolve('zz-test-web-only'))   # terminal-only, hidden on web


if __name__ == '__main__':
    unittest.main()

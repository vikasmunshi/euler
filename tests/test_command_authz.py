#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Unit tests for the per-profile command authorization layer (solver.shell.command)."""
from __future__ import annotations

import contextlib
import unittest
from typing import Iterator

from solver.config import config
from solver.shell.command import Context, _authorization_policy, command, is_authorized, registry


@contextlib.contextmanager
def as_profile(profile: str) -> Iterator[None]:
    """Temporarily run under *profile* (the authz check reads config.user_profile live)."""
    saved = config.user_profile
    config.user_profile = profile
    try:
        yield
    finally:
        config.user_profile = saved


class AuthorizationPolicyTests(unittest.TestCase):
    def test_policy_parses_commands_csv(self) -> None:
        policy = _authorization_policy()
        self.assertEqual(policy['users'], frozenset({'admin'}))            # admin-only
        self.assertEqual(policy['benchmark'], frozenset({'admin', 'user'}))  # not guest
        self.assertEqual(policy['?'], frozenset({'admin', 'user', 'guest'}))  # everyone

    def test_is_authorized_respects_profile(self) -> None:
        with as_profile('guest'):
            self.assertTrue(is_authorized('?'))          # read-only, granted to guest
            self.assertFalse(is_authorized('benchmark'))  # user+ only
            self.assertFalse(is_authorized('users'))      # admin only
        with as_profile('user'):
            self.assertTrue(is_authorized('benchmark'))
            self.assertFalse(is_authorized('users'))
        with as_profile('admin'):
            self.assertTrue(is_authorized('users'))

    def test_unlisted_command_is_admin_only(self) -> None:
        with as_profile('guest'):
            self.assertFalse(is_authorized('brand-new-command'))
        with as_profile('user'):
            self.assertFalse(is_authorized('brand-new-command'))
        with as_profile('admin'):
            self.assertTrue(is_authorized('brand-new-command'))   # fail-safe: admin still gets it


class DecoratorEnforcementTests(unittest.TestCase):
    def tearDown(self) -> None:
        for name in ('zz-test-cmd-guest', 'zz-test-cmd-admin'):
            registry.unregister(name)

    def test_unauthorized_command_is_not_registered(self) -> None:
        with as_profile('guest'):
            @command(name='zz-test-cmd-guest')            # unlisted → admin-only → skipped for guest
            def _f(ctx: Context) -> int:
                return 0
        self.assertIsNone(registry.resolve('zz-test-cmd-guest'))  # invisible to help/dispatch
        self.assertEqual(_f(Context()), 0)                        # still a working callable

    def test_authorized_command_is_registered(self) -> None:
        with as_profile('admin'):
            @command(name='zz-test-cmd-admin')
            def _f(ctx: Context) -> int:
                return 0
        self.assertIsNotNone(registry.resolve('zz-test-cmd-admin'))


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The shutdown notice: when one instance's countdown closes its shell, and how `logout-all`
drives every instance. The clock runs on short real waits against a fake manager, so a test
says what the shell is doing and reads what the terminals were told."""
from __future__ import annotations

import asyncio
import json
import unittest
from typing import Any, cast
from unittest.mock import patch

from euler_webshell import logout_all, users
from euler_webshell.user.logout import LogoutNotice
from euler_webshell.ws.manager import PtyManager
from tests import silence

silence()

_TICK = 0.01


class _Manager:
    """A stand-in :class:`PtyManager`: one shell, whose state a test sets directly."""

    def __init__(self, running: bool = False, attached: int = 1, alive: bool = True) -> None:
        self.running, self.attached, self.alive = running, attached, alive
        self.frames: list[dict[str, Any]] = []
        self.closed = False

    def snapshot(self) -> list[dict[str, object]]:
        if self.closed or not self.alive:
            return []
        return [{'alive': True, 'running': self.running, 'attached': self.attached}]

    async def notify_all(self, message: str) -> int:
        self.frames.append(json.loads(message))
        return 1

    async def close_all(self) -> None:
        self.closed = True


class NoticeTests(unittest.IsolatedAsyncioTestCase):
    def notice(self, manager: _Manager) -> LogoutNotice:
        self.ended = 0

        def on_end() -> None:
            self.ended += 1

        notice = LogoutNotice(cast(PtyManager, manager), on_end, tick=_TICK)
        self.addAsyncCleanup(notice.cancel)
        return notice

    async def settle(self, notice: LogoutNotice) -> None:
        async with asyncio.timeout(5):
            while notice.active:
                await asyncio.sleep(_TICK)

    async def test_an_idle_shell_closes_when_the_countdown_ends(self) -> None:
        manager = _Manager()
        notice = self.notice(manager)
        notice.arm('stopping', 0, 60)
        await self.settle(notice)
        self.assertTrue(manager.closed)
        self.assertEqual(manager.frames[-1], {'euler': 'logout-end'})
        self.assertEqual(self.ended, 1, 'the vault key goes with the shell')

    async def test_terminals_are_told_the_reason_and_the_time(self) -> None:
        manager = _Manager()
        notice = self.notice(manager)
        notice.arm('stopping', 60, 600)
        await asyncio.sleep(_TICK * 3)
        self.assertEqual(manager.frames[0], {'euler': 'logout', 'reason': 'stopping', 'running': False,
                                             'remaining': 60})
        self.assertFalse(manager.closed)

    async def test_with_no_terminal_an_idle_shell_closes_at_once(self) -> None:
        manager = _Manager(attached=0)
        notice = self.notice(manager)
        notice.arm('stopping', 60, 600)
        await self.settle(notice)
        self.assertTrue(manager.closed)

    async def test_running_work_holds_the_shell_past_the_countdown(self) -> None:
        manager = _Manager(running=True)
        notice = self.notice(manager)
        notice.arm('stopping', 0, 60)
        await asyncio.sleep(_TICK * 5)
        self.assertFalse(manager.closed)
        self.assertEqual(manager.frames[-1]['remaining'], 60, 'the page is told the limit')
        manager.running = False
        await self.settle(notice)
        self.assertTrue(manager.closed)

    async def test_detached_running_work_holds_it_too(self) -> None:
        manager = _Manager(running=True, attached=0)
        notice = self.notice(manager)
        notice.arm('stopping', 60, 600)
        await asyncio.sleep(_TICK * 5)
        self.assertFalse(manager.closed)

    async def test_the_limit_ends_running_work(self) -> None:
        manager = _Manager(running=True)
        notice = self.notice(manager)
        notice.arm('stopping', 0, 0)
        await self.settle(notice)
        self.assertTrue(manager.closed)

    async def test_now_ends_running_work_at_once(self) -> None:
        manager = _Manager(running=True)
        notice = self.notice(manager)
        notice.arm('stopping', 60, 600)
        await asyncio.sleep(_TICK)
        notice.now()
        await self.settle(notice)
        self.assertTrue(manager.closed)

    async def test_now_with_no_notice_standing_still_closes_the_shell(self) -> None:
        manager = _Manager(running=True)
        notice = self.notice(manager)
        notice.now()
        await self.settle(notice)
        self.assertTrue(manager.closed)
        self.assertEqual(manager.frames, [{'euler': 'logout-end'}], 'open tabs still sign out')
        self.assertEqual(self.ended, 1, 'the vault key goes with the shell')

    async def test_no_notice_standing_reports_no_time_left(self) -> None:
        manager = _Manager()
        notice = self.notice(manager)
        notice.arm('stopping', 0, 600)
        await self.settle(notice)
        manager.closed, manager.running = False, True      # the user is back, and busy
        self.assertEqual(notice.status()['remaining'], 0)

    async def test_extend_moves_the_countdown_and_the_limit(self) -> None:
        manager = _Manager(running=True)
        notice = self.notice(manager)
        notice.arm('stopping', 0, 0)
        notice.extend(60)
        await asyncio.sleep(_TICK * 5)
        self.assertFalse(manager.closed, 'the limit moved')
        manager.running = False
        await asyncio.sleep(_TICK * 5)
        self.assertFalse(manager.closed, 'the countdown moved')

    async def test_arming_twice_keeps_the_first_clock(self) -> None:
        manager = _Manager()
        notice = self.notice(manager)
        notice.arm('first', 60, 600)
        notice.arm('second', 0, 0)
        await asyncio.sleep(_TICK * 3)
        self.assertFalse(manager.closed)
        self.assertEqual(manager.frames[-1]['reason'], 'first')

    async def test_a_shell_already_gone_ends_the_notice(self) -> None:
        manager = _Manager()
        notice = self.notice(manager)
        notice.arm('stopping', 60, 600)
        manager.alive = False                    # the user signed out from the notice
        await self.settle(notice)
        self.assertEqual(manager.frames.count({'euler': 'logout-end'}), 0)
        self.assertEqual(self.ended, 1)


class CommandTests(unittest.TestCase):
    def setUp(self) -> None:
        self.launch = self.enterContext(patch('euler_webshell.users.subprocess.run'))
        self.launch.return_value.returncode = 0
        self.printed = self.enterContext(patch('euler_webshell.users.console.print'))

    def said(self) -> str:
        return ' '.join(str(call.args[0]) for call in self.printed.call_args_list)

    def test_a_reason_with_now_is_called_out(self) -> None:
        self.assertEqual(users.logout_all('stopping', now=True), 0)
        self.assertIn('--now', self.launch.call_args.args[0])
        self.assertIn('reason goes unused', self.said())

    def test_a_reason_with_extend_is_called_out(self) -> None:
        users.logout_all('stopping', extend=60)
        self.assertIn('reason goes unused', self.said())

    def test_the_default_reason_says_nothing(self) -> None:
        users.logout_all(now=True)
        self.assertEqual(self.said(), '')

    def test_a_notice_keeps_its_reason_without_comment(self) -> None:
        users.logout_all('stopping')
        self.assertIn('stopping', self.launch.call_args.args[0])
        self.assertEqual(self.said(), '')

    def test_ctrl_c_is_an_interruption_not_an_error(self) -> None:
        self.launch.side_effect = KeyboardInterrupt
        self.assertEqual(users.logout_all('stopping'), 130)
        self.assertIn('interrupted', self.said())
        self.assertNotIn('error', self.said())

    def test_a_failed_launch_is_still_an_error(self) -> None:
        self.launch.side_effect = OSError('no sudo')
        self.assertEqual(users.logout_all('stopping'), 1)
        self.assertIn('no sudo', self.said())


class LogoutAllTests(unittest.TestCase):
    def setUp(self) -> None:
        self.calls: list[tuple[str, str, dict[str, Any] | None]] = []
        self.states: dict[str, list[dict[str, Any] | None]] = {}
        self.enterContext(patch.object(logout_all, '_POLL_SECONDS', 0))
        self.enterContext(patch.object(logout_all, '_call', self.fake_call))
        self.enterContext(patch.object(logout_all, 'running_instances', lambda: ['ann', 'bob']))
        self.revoke = self.enterContext(patch.object(logout_all, 'revoke_all', return_value=3))
        self.enterContext(patch('builtins.print'))

    def fake_call(self, slug: str, method: str, body: dict[str, Any] | None = None) -> dict[str, Any] | None:
        self.calls.append((slug, method, body))
        if method == 'POST':
            return {'active': True}
        queue = self.states.get(slug, [])
        return queue.pop(0) if queue else {'active': False}

    def posts(self) -> list[tuple[str, dict[str, Any] | None]]:
        return [(slug, body) for slug, method, body in self.calls if method == 'POST']

    def test_it_arms_everyone_waits_then_revokes(self) -> None:
        self.states['ann'] = [{'active': True, 'running': True}]
        self.assertEqual(logout_all.main(['stopping']), 0)
        armed = {'reason': 'stopping', 'seconds': logout_all.DEFAULT_SECONDS, 'limit': logout_all.DEFAULT_LIMIT}
        self.assertEqual(self.posts(), [('ann', armed), ('bob', armed)])
        self.assertEqual(sum(1 for slug, method, _ in self.calls if slug == 'ann' and method == 'GET'), 2)
        self.revoke.assert_called_once()

    def test_extend_adds_time_and_leaves_the_rest_to_the_waiting_run(self) -> None:
        self.assertEqual(logout_all.main(['--extend=120']), 0)
        self.assertEqual(self.posts(), [('ann', {'extend': 120}), ('bob', {'extend': 120})])
        self.revoke.assert_not_called()

    def test_now_finishes_the_job_itself(self) -> None:
        self.assertEqual(logout_all.main(['--now']), 0)
        self.assertEqual(self.posts(), [('ann', {'now': True}), ('bob', {'now': True})])
        self.revoke.assert_called_once()

    def test_an_instance_that_goes_away_stops_being_waited_on(self) -> None:
        self.states['ann'] = [None]
        self.assertEqual(logout_all.main([]), 0)
        self.revoke.assert_called_once()

    def test_a_failed_revoke_is_reported(self) -> None:
        self.revoke.side_effect = RuntimeError('refused')
        self.assertEqual(logout_all.main([]), 1)

    def test_stopping_the_wait_revokes_nothing(self) -> None:
        with patch.object(logout_all, '_wait', side_effect=KeyboardInterrupt):
            self.assertEqual(logout_all.main([]), 130)
        self.revoke.assert_not_called()


class RunningInstancesTests(unittest.TestCase):
    def test_the_slugs_come_from_the_active_units(self) -> None:
        listing = ('euler-user@ann.service loaded active running euler user\n'
                   'euler-user@bob.service loaded active running euler user\n')
        with patch('subprocess.run') as run:
            run.return_value.stdout = listing
            self.assertEqual(logout_all.running_instances(), ['ann', 'bob'])

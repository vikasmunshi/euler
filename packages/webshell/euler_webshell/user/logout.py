#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The shutdown notice: one instance's countdown to closing its shell (`logout-all`).

The operator's push (:mod:`euler_webshell.logout_all`) arms it over `/internal/logout-notice`,
and the instance keeps the clock, so a later `--extend` or `--now` from any terminal just talks
to the same state. It ticks to every attached terminal over text frames, which the replay
never carries, and `terminal.js` draws them.

The shell closes at the first of:

- the countdown ending with the shell idle — at once if no terminal is attached, since nobody
  is reading the countdown;
- the limit, with or without running work: waiting counts as running, so an idle `claude` would
  otherwise hold a shutdown for ever;
- `--now`, which needs no notice standing: with none it closes the shell just the same.

Running work past the countdown extends the wait on its own, up to the limit. The final frame
tells open tabs to sign out; a user with no tab open is signed out by the operator's push.
"""
from __future__ import annotations

__all__ = ['LogoutNotice']

import asyncio
import json
import logging
import time
from typing import Callable

from euler_webshell.ws.manager import PtyManager

log = logging.getLogger('euler-user')


class LogoutNotice:
    """The countdown on one instance: armed once, then extended, forced or run out."""

    def __init__(self, manager: PtyManager, on_end: Callable[[], None], tick: float = 1.0) -> None:
        self._manager = manager
        self._on_end = on_end
        self._tick = tick
        self._task: asyncio.Task[None] | None = None
        self._wake = asyncio.Event()
        self._forced = False
        self._reason = ''
        self._deadline = 0.0
        self._limit = 0.0

    @property
    def active(self) -> bool:
        """True from arming until the shell has closed."""
        return self._task is not None and not self._task.done()

    def arm(self, reason: str, seconds: int, limit: int) -> None:
        """Start the countdown; a notice already running keeps its clock."""
        if self.active:
            return
        now = time.monotonic()
        self._reason = reason
        self._deadline = now + seconds
        self._limit = now + max(seconds, limit)
        self._forced = False
        self._wake.clear()
        self._task = asyncio.create_task(self._run())

    def extend(self, seconds: int) -> None:
        """Add *seconds* to the countdown and the limit: past the limit, the operator decides."""
        self._deadline = max(self._deadline, time.monotonic()) + seconds
        self._limit += seconds

    def now(self) -> None:
        """Close the shell at once, running work or not, with or without a notice standing."""
        if not self.active:
            self.arm('', 0, 0)
        self._forced = True
        self._wake.set()

    def status(self) -> dict[str, object]:
        """Where the notice stands, for the operator's wait."""
        running = self._running()
        return {'active': self.active, 'running': running,
                'remaining': self._remaining(running) if self.active else 0}

    async def cancel(self) -> None:
        """Stop the clock (service stop: the shells are closed by the cleanup that follows)."""
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    def _running(self) -> bool:
        return any(shell['running'] for shell in self._manager.snapshot())

    def _remaining(self, running: bool) -> int:
        """Seconds to the moment the page should name: the limit while work runs."""
        return max(0, round((self._limit if running else self._deadline) - time.monotonic()))

    def _due(self, running: bool, attached: bool) -> bool:
        now = time.monotonic()
        if self._forced or now >= self._limit:
            return True
        return not running and (now >= self._deadline or not attached)

    async def _run(self) -> None:
        try:
            while True:
                shells = [shell for shell in self._manager.snapshot() if shell['alive']]
                if not shells:                   # none to warn, or the user already signed out
                    break
                running = any(shell['running'] for shell in shells)
                if self._due(running, any(shell['attached'] for shell in shells)):
                    await self._manager.notify_all(json.dumps({'euler': 'logout-end'}))
                    await self._manager.close_all()
                    break
                await self._manager.notify_all(json.dumps({
                    'euler': 'logout', 'reason': self._reason, 'running': running,
                    'remaining': self._remaining(running)}))
                try:
                    await asyncio.wait_for(self._wake.wait(), timeout=self._tick)
                except TimeoutError:
                    pass
        except Exception:                        # noqa: BLE001 — the key must still be dropped
            log.exception('logout notice failed')
        self._on_end()

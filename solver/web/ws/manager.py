#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Persistent per-user PTY shells: one long-lived solver shell per web user (DD-14).

A browser terminal (``GET /ws``) attaches to the signed-in user's shell rather
than forking a throwaway one. The PTY's lifetime is decoupled from any single
WebSocket: the shell keeps running across disconnects and reconnects, and is
torn down only by in-shell ``exit``, the auth service's logout/revocation push
(``POST /internal/logout``), or service stop. At most one shell exists per user
*per instance* — a second browser tab for the same user attaches to the *same*
shell (a shared terminal, like ``tmux attach`` twice).

:class:`PtyManager` owns the shells, keyed by user email. Each
:class:`PersistentPty` runs a single background *drainer* task that reads the
PTY master continuously — whether or not anyone is attached, so the shell never
blocks on a full kernel buffer while disconnected — appending output to a
bounded replay buffer and fanning it out to every attached socket. On
(re)attach the buffer is replayed so the reconnecting terminal redraws its
recent scrollback and live prompt instead of a blank screen.
"""
from __future__ import annotations

__all__ = ['PersistentPty', 'PtyManager']

import asyncio
import time
from typing import Awaitable, Callable

from aiohttp import web

from solver.web.ws.pty import PtySession

#: Cap (bytes) on the per-shell replay buffer sent to a (re)attaching terminal.
_REPLAY_CAP: int = 256 * 1024


class PersistentPty:
    """One user's long-lived PTY shell, shared by any number of attached sockets.

    A single background drainer task (`_drain`) owns all reads from the PTY
    master, so byte order is well-defined and the shell keeps making progress
    even with no client attached. Output is mirrored into a bounded buffer for
    replay on the next attach.
    """

    def __init__(self, session: PtySession, buffer_cap: int = _REPLAY_CAP) -> None:
        self.session = session
        self._subscribers: set[web.WebSocketResponse] = set()
        self._buffer = bytearray()
        self._cap = buffer_cap
        self._reader: asyncio.Task[None] | None = None
        self._closed = False
        self._detached_since: float = time.monotonic()  # zero subscribers since (DD-14 reaper)

    def start(self) -> None:
        """Launch the background drainer task (call once, right after construction)."""
        self._reader = asyncio.create_task(self._drain())

    @property
    def alive(self) -> bool:
        """True while the shell has not been torn down and its process is running."""
        return not self._closed and self.session.is_alive()

    @property
    def detached_for(self) -> float:
        """Seconds this shell has had zero attached sockets (0.0 while attached)."""
        return 0.0 if self._subscribers else time.monotonic() - self._detached_since

    # -- output path --------------------------------------------------------

    def _append(self, data: bytes) -> None:
        """Append output to the replay buffer, trimming to the newest `_cap` bytes."""
        self._buffer.extend(data)
        if len(self._buffer) > self._cap:
            del self._buffer[:len(self._buffer) - self._cap]

    async def _broadcast(self, data: bytes) -> None:
        """Send *data* to every attached socket, dropping any that have gone away."""
        for ws in list(self._subscribers):
            if ws.closed:
                self.detach(ws)
                continue
            try:
                await ws.send_bytes(data)
            except (ConnectionError, RuntimeError):
                self.detach(ws)

    async def _drain(self) -> None:
        """Continuously read the PTY, buffering and fanning out until the shell exits."""
        loop = asyncio.get_running_loop()
        while True:
            data = await loop.run_in_executor(None, self.session.read)
            if not data:  # empty read → the shell process has exited
                break
            self._append(data)
            await self._broadcast(data)
        await self._shutdown(b'shell exited')

    async def _shutdown(self, notify: bytes) -> None:
        """Close every attached socket and terminate the PTY (idempotent)."""
        if self._closed:
            return
        self._closed = True
        for ws in list(self._subscribers):
            try:
                await ws.close(message=notify)
            except Exception:  # noqa: BLE001 — best-effort socket teardown
                pass
        self._subscribers.clear()
        self.session.close()

    # -- attach / input -----------------------------------------------------

    async def attach(self, ws: web.WebSocketResponse) -> None:
        """Register *ws* and replay the recent output so it redraws immediately."""
        self._subscribers.add(ws)
        if self._buffer and not ws.closed:
            try:
                await ws.send_bytes(bytes(self._buffer))
            except (ConnectionError, RuntimeError):
                self.detach(ws)

    def detach(self, ws: web.WebSocketResponse) -> None:
        """Stop forwarding to *ws*; the shell keeps running for other/later clients."""
        self._subscribers.discard(ws)
        if not self._subscribers:
            self._detached_since = time.monotonic()

    def write(self, data: bytes) -> None:
        """Forward keystrokes from an attached terminal to the shared shell."""
        self.session.write(data)

    def resize(self, cols: int, rows: int) -> None:
        """Resize the shared PTY (any attached tab drives the geometry for all)."""
        self.session.resize(cols=cols, rows=rows)

    async def close(self) -> None:
        """Terminate the shell and its drainer (logout/revocation push, server stop).

        Closing the session kills the child, which ends the blocking read in the
        drainer; awaiting the drainer lets it run its own `_shutdown`. A final
        `_shutdown` is a no-op if that already happened.
        """
        self.session.close()  # kill the child → the drainer's read returns EOF
        if self._reader is not None:
            try:
                await self._reader
            except Exception:  # noqa: BLE001 — drainer teardown must not propagate
                pass
            self._reader = None
        await self._shutdown(b'shell terminated')


class PtyManager:
    """Owns one :class:`PersistentPty` per user email; forks lazily, reaps on demand."""

    def __init__(self) -> None:
        self._shells: dict[str, PersistentPty] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    async def get_or_create(self, email: str,
                            spawn: Callable[[], Awaitable[PtySession]]) -> PersistentPty:
        """Return the user's live shell, forking a fresh one via *spawn* if none is.

        *spawn* is awaited only when a new shell is actually needed — it mints the
        single-use ticket and forks (DD-9), so an attach to an existing shell
        consumes no ticket. The per-email lock serialises concurrent first
        attaches (two tabs opened together fork exactly one shell).
        """
        lock = self._locks.setdefault(email, asyncio.Lock())
        async with lock:
            pty = self._shells.get(email)
            if pty is not None and pty.alive:
                return pty
            pty = PersistentPty(await spawn())
            pty.start()
            self._shells[email] = pty
            return pty

    async def close(self, email: str) -> bool:
        """Terminate and forget the user's shell, if any (logout/revocation push)."""
        pty = self._shells.pop(email, None)
        if pty is None:
            return False
        await pty.close()
        return True

    async def close_all(self) -> None:
        """Terminate every shell (server stop / app cleanup)."""
        shells = list(self._shells.values())
        self._shells.clear()
        for pty in shells:
            await pty.close()

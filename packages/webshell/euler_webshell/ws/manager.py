#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Persistent per-user PTY shells: one long-lived solver shell per web user.

A browser terminal (`GET /ws`) attaches to the signed-in user's shell rather
than forking a throwaway one. The PTY's lifetime is decoupled from any single
WebSocket: the shell keeps running across disconnects and reconnects, and is
torn down only by in-shell `exit`, the auth service's logout/revocation push
(`POST /internal/logout`), or service stop. At most one shell exists per user
*per instance* — a second browser tab for the same user attaches to the *same*
shell (a shared terminal, like `tmux attach` twice).

:class:`PtyManager` owns the shells, keyed by user email. Each
:class:`PersistentPty` runs a single background *drainer* task that reads the
PTY master continuously — whether or not anyone is attached, so the shell never
blocks on a full kernel buffer while disconnected — appending output to a
bounded replay buffer and fanning it out to every attached socket. On
(re)attach the buffer is replayed so the reconnecting terminal redraws its
recent scrollback and live prompt instead of a blank screen.

The buffer is bounded, so a long session can push out the sequence that set a terminal
*mode* while the mode still holds — the `busy` that lent the PTY to `claude`, the kitty
keyboard flags and the focus and mouse reporting `claude` turned on. :class:`TermModes`
watches the same stream and the replay's end frame carries what it saw, so a reattach
restores the state the replay alone can no longer promise.
"""
from __future__ import annotations

__all__ = ['PersistentPty', 'PtyManager', 'TermModes', 'replay_end']

import asyncio
import json
import re
import time
from typing import Awaitable, Callable

from aiohttp import web

from euler_webshell.ws.pty import PtySession

#: Cap (bytes) on the per-shell replay buffer sent to a (re)attaching terminal.
_REPLAY_CAP: int = 256 * 1024


#: The sequences :class:`TermModes` follows: the web shell's OSC 5379 `busy` / `ready`
#: (group 1 the key, 2 the state), the keyboard-mode CSIs terminal.js obeys — kitty's
#: `CSI > f u` / `CSI < n u` / `CSI = f ; m u` and XTMODKEYS `CSI > r ; v m` (group 3 the
#: prefix, 4 the parameters, 5 the final) — DECSET / DECRST `CSI ? n ; … h|l` (group 6
#: the modes, 7 set or reset), and RIS `ESC c`, the full reset (group 8).
_MODE_RE = re.compile(rb'\x1b\]5379;([^;\x07\x1b]*);(busy|ready)[^\x07\x1b]*\x07'
                      rb'|\x1b\[([<>=])([0-9;]*)([um])'
                      rb'|\x1b\[\?([0-9;]*)([hl])'
                      rb'|\x1b(c)')

#: The DEC private modes that make the terminal *write to the PTY unasked*: X10 and the
#: three mouse-tracking protocols (one is active at a time, and resetting any of them turns
#: tracking off, as in xterm.js), focus reporting (1004), and bracketed paste (2004) — plus
#: SGR mouse encoding (1006), which says how the mouse reports are spelled. A stale one
#: sends the solver's prompt bytes it never asked for (`ESC [ O` on every blur), so these
#: are the modes a reattach restores. Screen modes (the alternate screen, the cursor) the
#: replay redraws well enough on its own.
_MOUSE_PROTOCOLS: frozenset[int] = frozenset({9, 1000, 1002, 1003})
_FOCUS, _PASTE, _SGR_MOUSE = 1004, 2004, 1006

#: A sequence split across two PTY reads is held back at most this long (bytes) awaiting
#: its end; the longest one followed here — the OSC, with its 32-hex key — is under 80.
_MODE_CARRY: int = 256

#: The kitty flag stack's depth bound. The protocol lets a terminal cap it; this one keeps
#: an app that pushes without popping from growing it without end.
_KITTY_DEPTH: int = 16


class TermModes:
    """The terminal state a reattach must restore, kept from the whole PTY stream.

    The replay rebuilds it in the browser too (terminal.js), but only from the bytes the
    buffer still holds: after a long session the `busy` that lent the PTY to `claude` has
    scrolled out while `claude` still runs, and the page comes back offering to type into
    it. This sees every byte, so it does not forget — and it is the shell's state, not one
    tab's, so it is right for a second tab, another device, or a browser restarted since.

    It mirrors terminal.js's handlers exactly (§ the OSC handler, § modified Enter), and
    :meth:`snapshot` is what the replay's end frame carries for the page to adopt.
    """

    def __init__(self, osc_key: str) -> None:
        self._key = osc_key.encode()
        self.busy = False
        self.kitty: list[int] = [0]       # the kitty flag stack; [0] is the base entry
        self.other_keys = 0               # xterm's modifyOtherKeys level (0 = off)
        self.mouse = 0                    # the active mouse protocol's mode (0 = off)
        self.sgr_mouse = False            # mouse reports in SGR encoding (1006)
        self.focus = False                # focus in/out reports (1004)
        self.paste = False                # bracketed paste (2004)
        self._pending = b''

    def feed(self, data: bytes) -> None:
        """Follow one PTY read. A sequence cut by the read's edge is held for the next."""
        data = self._pending + data
        end = 0
        for match in _MODE_RE.finditer(data):
            self._apply(match)
            end = match.end()
        tail = data[end:]
        esc = tail.rfind(b'\x1b')
        self._pending = tail[esc:] if esc != -1 and len(tail) - esc <= _MODE_CARRY else b''

    def _apply(self, match: re.Match[bytes]) -> None:
        key, state, prefix, raw, final, dec, setting, reset = match.groups()
        if reset is not None:
            self.mouse, self.sgr_mouse, self.focus, self.paste = 0, False, False, False
            return
        if dec is not None:
            self._dec(dec, setting == b'h')
            return
        if state is not None:
            if self._key and key == self._key:    # printed text does not know the key
                self.busy = state == b'busy'
            return
        params = [int(p) if p else None for p in raw.split(b';')]

        def param(index: int, fallback: int) -> int:
            value = params[index] if index < len(params) else None
            return fallback if value is None else value

        if final == b'm':
            if prefix == b'>':
                resource = param(0, 0)
                if resource == 0:
                    self.other_keys = 0
                elif resource == 4:
                    self.other_keys = param(1, 0)
        elif prefix == b'>':
            self.kitty.append(param(0, 0))
            if len(self.kitty) > _KITTY_DEPTH:
                del self.kitty[1]
        elif prefix == b'<':
            count = param(0, 1) or 1
            while count > 0 and len(self.kitty) > 1:
                self.kitty.pop()
                count -= 1
        else:                                     # '=': 1 assign, 2 set bits, 3 clear bits
            flags, mode = param(0, 0), param(1, 1) or 1
            top = self.kitty[-1]
            self.kitty[-1] = top | flags if mode == 2 else top & ~flags if mode == 3 else flags

    def _dec(self, raw: bytes, on: bool) -> None:
        """Follow one DECSET (*on*) or DECRST: only the modes in § `_MOUSE_PROTOCOLS` above."""
        for mode in (int(p) for p in raw.split(b';') if p):
            if mode in _MOUSE_PROTOCOLS:
                self.mouse = mode if on else 0
            elif mode == _SGR_MOUSE:
                self.sgr_mouse = on
            elif mode == _FOCUS:
                self.focus = on
            elif mode == _PASTE:
                self.paste = on

    def snapshot(self) -> dict[str, object]:
        """The state as the replay's end frame carries it (terminal.js adopts it)."""
        return {'busy': self.busy, 'kitty': list(self.kitty), 'otherKeys': self.other_keys,
                'mouse': self.mouse, 'sgrMouse': self.sgr_mouse, 'focus': self.focus,
                'paste': self.paste}


def replay_end(osc_key: str, modes: TermModes | None = None) -> str:
    """The text frame closing the replay on attach, carrying the shell's OSC key.

    Everything before it is scrollback, everything after is live. The client must not act
    on control sequences carried by the replay (an already-run `show` would re-navigate the
    pane on every load) — see :meth:`PersistentPty.attach`. And a text frame never enters
    the replay buffer and cannot be written by the PTY, so the key reaches the page by a
    path no printed text can imitate.

    With *modes* it also carries the terminal's state (:class:`TermModes`), which the page
    adopts over whatever the replay rebuilt — the replay may have lost the sequence that
    set it.
    """
    return json.dumps({'replay': 'end', 'osc': osc_key, **(modes.snapshot() if modes else {})})


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
        self._detached_since: float = time.monotonic()  # zero subscribers since (the reaper)
        self._modes = TermModes(getattr(session, 'osc_key', ''))

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

    @property
    def attached(self) -> int:
        """How many browser terminals are currently attached (0 = running detached)."""
        return len(self._subscribers)

    # -- output path --------------------------------------------------------

    def _append(self, data: bytes) -> None:
        """Append output to the replay buffer, trimming to the newest `_cap` bytes.

        The modes are followed here too, before the trim: they outlive the bytes that set them.
        """
        self._modes.feed(data)
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
        """Register *ws* and replay the recent output so it redraws immediately.

        The replay is followed by the :func:`replay_end` marker — a text frame,
        so it cannot collide with the raw PTY byte stream. The client needs it:
        the buffer may contain the *control sequences* of commands already run
        (`show`/`edit` emit OSC 5379), and a terminal that acted on those
        again would hijack the pane on every page load — a deep link to one
        problem would bounce to whatever the shell last showed. Everything before
        the marker is scrollback to redraw; only what comes after is live.
        """
        self._subscribers.add(ws)
        if ws.closed:
            return
        try:
            if self._buffer:
                await ws.send_bytes(bytes(self._buffer))
            await ws.send_str(replay_end(getattr(self.session, 'osc_key', ''), self._modes))
        except (ConnectionError, RuntimeError):
            self.detach(ws)

    def detach(self, ws: web.WebSocketResponse) -> None:
        """Stop forwarding to *ws*; the shell keeps running for other/later clients."""
        self._subscribers.discard(ws)
        if not self._subscribers:
            self._detached_since = time.monotonic()

    async def notify(self, message: str) -> int:
        """Send a **text** frame to every attached socket; return how many took it.

        For out-of-band news the *page* must act on — today a message arriving for this
        user (:mod:`euler_webshell.user.msg_api`). It deliberately does not touch the PTY:
        a service-originated nudge written into the shell's byte stream would land in
        the replay buffer and re-fire on every reattach, which is the whole reason
        `OSC 5379` needs its monotonic token (:meth:`attach`). A text frame is not
        replayed, so it needs no token and cannot be mistaken for shell output.
        """
        sent = 0
        for ws in list(self._subscribers):
            if ws.closed:
                self.detach(ws)
                continue
            try:
                await ws.send_str(message)
                sent += 1
            except (ConnectionError, RuntimeError):
                self.detach(ws)
        return sent

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
        single-use ticket and forks, so an attach to an existing shell
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

    async def notify_all(self, message: str) -> int:
        """Send a text frame to every attached socket of every shell here.

        The per-user tier runs one instance per collaborator, so "every shell" is that
        one collaborator's — no key is needed and none is invented. Returns how many
        sockets took it, which is 0 for a user with no terminal open: the nudge is only
        a nudge, and the count they missed is rendered server-side on their next load.
        """
        sent = 0
        for pty in list(self._shells.values()):
            sent += await pty.notify(message)
        return sent

    async def reap_detached(self, ttl_seconds: int) -> list[str]:
        """Close and forget shells with **zero attached sockets** for longer than
        *ttl_seconds*; return the reaped emails (hygiene, not security).

        A shell keeps running while detached so a long benchmark survives a closed
        laptop and a reconnect replays — but a shell nobody has reattached to in a
        day is almost certainly abandoned, so it is reaped to free the process. The
        stale set is materialised before closing (`close` mutates the dict).
        """
        if ttl_seconds <= 0:
            return []
        stale = [email for email, pty in self._shells.items()
                 if pty.detached_for > ttl_seconds]
        for email in stale:
            await self.close(email)
        return stale

    def snapshot(self) -> list[dict[str, object]]:
        """Describe every shell this manager holds — the operator's `status-web` view.

        One record per shell: whose it is, whether the process is still alive, how many
        terminals are attached right now, and how long it has been running with none.
        Read-only and allocation-cheap; the reporting path (`GET /internal/status`)
        must never disturb a live shell.
        """
        return [{'user': email,
                 'alive': pty.alive,
                 'attached': pty.attached,
                 'detached_for': round(pty.detached_for, 1),
                 'pid': pty.session.pid}
                for email, pty in self._shells.items()]

    async def close_all(self) -> None:
        """Terminate every shell (server stop / app cleanup)."""
        shells = list(self._shells.values())
        self._shells.clear()
        for pty in shells:
            await pty.close()

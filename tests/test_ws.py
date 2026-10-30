#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Tests for the web-shell service.

Covers the attach path end-to-end against a **fake auth service** on a unix
socket (real :class:`~euler_site.auth.tickets.TicketStore` semantics — mint
gated on the session cookie, redeem single-use): identity/pin refusals, the
ticket-then-fork flow, the binary/resize wire protocol, replay + shared attach
for a second tab, mint-refusal close, and the `/internal/logout` teardown
push. The PTY child is a stub echo shell so the suite stays fast; one
integration test forks the **real** `python -m euler_webshell.shell` and drives it over the
ticket plane (the child redeems against the fake socket via
`EULER_AUTH_SOCKET`).
"""
from __future__ import annotations

import asyncio
import json
import os
import select
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import aiohttp
from aiohttp import WSMsgType, web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from euler_site.auth.tickets import TicketStore
from euler_webshell.ws.app import PTY_MANAGER, build_app
from euler_webshell.ws.manager import TermModes
from euler_webshell.ws.config import WsConfig
from euler_webshell.ws.pty import PtySession
from tests import silence

silence()   # quiet the attach-refused logging + filter aiohttp's request-key warning

_EMAIL = 'user@example.com'
_GOOD_COOKIE = 'solver_session=GOOD'
_HEADERS = {'X-User': _EMAIL, 'X-Profile': 'contributor', 'Cookie': _GOOD_COOKIE}

#: A minimal line-oriented stand-in for the solver shell: banner with the env it
#: received, echo with a marker, report its PTY size on demand, quit on 'exit'.
_STUB_CODE = """
import os, sys
print(f"BANNER ticket_len={len(os.environ.get('SOLVER_TICKET',''))} "
      f"profile={os.environ.get('EULER_PROFILE','')} "
      f"auth_socket={os.environ.get('EULER_AUTH_SOCKET','')} "
      f"solver_user={os.environ.get('SOLVER_USER','-none-')}", flush=True)
for line in sys.stdin:
    line = line.strip()
    if line == 'exit':
        break
    if line == 'size':
        size = os.get_terminal_size(0)
        print(f"SIZE {size.columns}x{size.lines}", flush=True)
    elif line:
        print('GOT:' + line, flush=True)
"""
_STUB_ARGV = (sys.executable, '-u', '-c', _STUB_CODE)


#: A deterministic policy for tests: the ladder plus an empty users map. Tests must
#: point EULER_AUTHZ_FILE at this — a host with the real /etc/euler SoR deployed would
#: otherwise leak its own user map into the run.
_AUTHZ_FIXTURE = Path(__file__).parent / 'fixtures' / 'authorizations.json'


class _FakeAuth:
    """The auth service's shell-ticket surface, on a unix socket."""

    def __init__(self) -> None:
        self.store = TicketStore()
        self.mints = 0

    def build(self) -> web.Application:
        async def mint(request: web.Request) -> web.Response:
            if request.headers.get('Cookie', '') != _GOOD_COOKIE:
                return web.Response(status=401, text='no session')
            self.mints += 1
            return web.json_response({'ticket': self.store.mint(_EMAIL, 'contributor')})

        async def redeem(request: web.Request) -> web.Response:
            body = await request.json()
            redeemed = self.store.redeem(str(body.get('ticket', '')))
            if redeemed is None:
                return web.Response(status=401, text='invalid ticket')
            return web.json_response({'email': redeemed[0], 'profile': redeemed[1]})

        app = web.Application()
        app.add_routes([web.post('/shell-ticket', mint),
                        web.post('/shell-ticket/redeem', redeem)])
        return app


async def _read_until(ws: aiohttp.ClientWebSocketResponse, needle: bytes,
                      timeout: float = 15.0) -> bytes:
    """Accumulate binary frames until *needle* appears (or the socket closes)."""
    buffer = b''
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    while needle not in buffer:
        msg = await asyncio.wait_for(ws.receive(), timeout=max(0.1, deadline - loop.time()))
        if msg.type == WSMsgType.BINARY:
            buffer += msg.data
        elif msg.type in (WSMsgType.CLOSE, WSMsgType.CLOSED, WSMsgType.ERROR):
            break
    return buffer


async def _read_text(ws: aiohttp.ClientWebSocketResponse, timeout: float = 15.0) -> str:
    """The next text frame (the control channel: today, the replay-end marker)."""
    while True:
        msg = await asyncio.wait_for(ws.receive(), timeout=timeout)
        if msg.type == WSMsgType.TEXT:
            return str(msg.data)
        if msg.type in (WSMsgType.CLOSE, WSMsgType.CLOSED, WSMsgType.ERROR):
            return ''


async def _read_close(ws: aiohttp.ClientWebSocketResponse, timeout: float = 15.0) -> None:
    """Drain frames until the server closes the socket."""
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    while True:
        msg = await asyncio.wait_for(ws.receive(), timeout=max(0.1, deadline - loop.time()))
        if msg.type in (WSMsgType.CLOSE, WSMsgType.CLOSED, WSMsgType.ERROR):
            return


class _WsServiceCase(AioHTTPTestCase):
    """Shared scaffolding: the fake auth socket + a pinned-policy ws app."""

    profile: str = 'contributor'
    shell_argv: tuple[str, ...] = _STUB_ARGV
    detached_ttl: int = 0                    # 0 disables the reaper (most tests)

    async def get_application(self) -> web.Application:
        # Deterministic policy: the bundled ladder (reader/contributor/maintainer/admin).
        os.environ['EULER_AUTHZ_FILE'] = str(_AUTHZ_FIXTURE)
        self.addCleanup(os.environ.pop, 'EULER_AUTHZ_FILE', None)

        scratch = Path(tempfile.mkdtemp(prefix='euler-ws-test-'))
        self.addCleanup(lambda: __import__('shutil').rmtree(scratch, True))
        self.auth = _FakeAuth()
        self.auth_socket = scratch / 'auth.sock'
        self._auth_runner = web.AppRunner(self.auth.build())
        await self._auth_runner.setup()
        await web.UnixSite(self._auth_runner, str(self.auth_socket)).start()

        config = WsConfig(socket_path=scratch / 'ws.sock', socket_group='', tcp_bind='',
                          profile=self.profile, auth_socket=str(self.auth_socket),
                          shell_argv=self.shell_argv, detached_ttl=self.detached_ttl)
        return build_app(config)

    async def tearDownAsync(self) -> None:
        await self._auth_runner.cleanup()
        await super().tearDownAsync()


class WsAttachTests(_WsServiceCase):
    """Identity, the wire protocol, sharing, and teardown — with the stub shell."""

    @unittest_run_loop
    async def test_healthz(self) -> None:
        response = await self.client.get('/healthz')
        self.assertEqual(response.status, 200)

    @unittest_run_loop
    async def test_unauthenticated_is_401(self) -> None:
        response = await self.client.get('/ws')
        self.assertEqual(response.status, 401)

    @unittest_run_loop
    async def test_pin_mismatch_is_401(self) -> None:
        response = await self.client.get(
            '/ws', headers={'X-User': _EMAIL, 'X-Profile': 'maintainer'})
        self.assertEqual(response.status, 401)

    @unittest_run_loop
    async def test_unknown_profile_is_401(self) -> None:
        response = await self.client.get(
            '/ws', headers={'X-User': _EMAIL, 'X-Profile': 'root'})
        self.assertEqual(response.status, 401)

    @unittest_run_loop
    async def test_attach_ticket_echo_and_resize(self) -> None:
        ws = await self.client.ws_connect('/ws', headers=_HEADERS)
        banner = await _read_until(ws, b'solver_user=')
        self.assertIn(b'ticket_len=43', banner)          # token_urlsafe(32) → 43 chars
        self.assertIn(b'profile=contributor', banner)    # the instance pin
        # The child must redeem against the socket the service minted from — not a
        # compiled-in default that is right only by accident of how it was configured.
        self.assertIn(f'auth_socket={self.auth_socket}'.encode(), banner)
        self.assertIn(b'solver_user=-none-', banner)     # display-only value is dropped
        self.assertEqual(self.auth.mints, 1)

        await ws.send_bytes(b'hello\n')
        self.assertIn(b'GOT:hello', await _read_until(ws, b'GOT:hello'))

        await ws.send_str('{"resize": [91, 33]}')
        await ws.send_bytes(b'size\n')
        self.assertIn(b'SIZE 91x33', await _read_until(ws, b'SIZE'))
        await ws.close()

    @unittest_run_loop
    async def test_attach_closes_the_replay_with_a_marker(self) -> None:
        """Every attach ends its replay with a text-frame marker, so the client can
        tell scrollback from live output — the replay carries the control sequences
        of commands that already ran (`show` → OSC 5379), and a terminal that obeyed
        them again would re-navigate the pane on every page load."""
        first = await self.client.ws_connect('/ws', headers=_HEADERS)
        opening = json.loads(await _read_text(first))   # even with no scrollback
        self.assertEqual(opening['replay'], 'end')
        self.assertRegex(opening['osc'], r'^[0-9a-f]{32}$', 'the shell\'s OSC key rides the marker')
        self.assertEqual((opening['busy'], opening['kitty'], opening['otherKeys']), (False, [0], 0))
        self.assertEqual((opening['mouse'], opening['focus'], opening['paste']), (0, False, False))
        await _read_until(first, b'BANNER')

        second = await self.client.ws_connect('/ws', headers=_HEADERS)   # replays
        seen, marker = b'', ''
        while not marker:                                # the marker follows the bytes
            msg = await asyncio.wait_for(second.receive(), timeout=10)
            if msg.type == WSMsgType.BINARY:
                seen += msg.data
            elif msg.type == WSMsgType.TEXT:
                marker = msg.data
        self.assertIn(b'BANNER', seen)                   # scrollback came first…
        self.assertEqual(json.loads(marker), opening)    # …then the boundary, same shell, same key
        await first.close()
        await second.close()

    @unittest_run_loop
    async def test_second_tab_shares_the_shell(self) -> None:
        first = await self.client.ws_connect('/ws', headers=_HEADERS)
        await _read_until(first, b'BANNER')

        second = await self.client.ws_connect('/ws', headers=_HEADERS)
        replay = await _read_until(second, b'BANNER')     # replay buffer, no new fork
        self.assertIn(b'BANNER', replay)
        self.assertEqual(self.auth.mints, 1)              # attach to existing = no new ticket

        await second.send_bytes(b'shared\n')              # both tabs see the one shell
        self.assertIn(b'GOT:shared', await _read_until(first, b'GOT:shared'))
        await first.close()
        await second.close()

    @unittest_run_loop
    async def test_mint_refusal_closes_the_socket(self) -> None:
        headers = {'X-User': _EMAIL, 'X-Profile': 'contributor', 'Cookie': 'solver_session=BAD'}
        ws = await self.client.ws_connect('/ws', headers=headers)
        await _read_close(ws)
        self.assertEqual(ws.close_code, aiohttp.WSCloseCode.POLICY_VIOLATION)
        self.assertEqual(self.auth.mints, 0)

    @unittest_run_loop
    async def test_internal_logout_tears_down(self) -> None:
        ws = await self.client.ws_connect('/ws', headers=_HEADERS)
        await _read_until(ws, b'BANNER')
        session = self.app[PTY_MANAGER]._shells[_EMAIL].session  # noqa: SLF001 — liveness probe

        response = await self.client.post('/internal/logout', json={'email': _EMAIL})
        self.assertEqual((await response.json())['closed'], True)
        await _read_close(ws)                             # the push closes attached sockets
        self.assertFalse(session.is_alive())              # …and the shell process itself

        response = await self.client.post('/internal/logout', json={'email': _EMAIL})
        self.assertEqual((await response.json())['closed'], False)   # idempotent

    @unittest_run_loop
    async def test_internal_logout_rejects_garbage(self) -> None:
        response = await self.client.post('/internal/logout', data=b'not json')
        self.assertEqual(response.status, 400)
        response = await self.client.post('/internal/logout', json={})
        self.assertEqual(response.status, 400)


class ReaderAttachTests(_WsServiceCase):
    """The reader floor: every rung may attach a terminal — attach works."""

    profile = 'reader'

    @unittest_run_loop
    async def test_reader_attaches(self) -> None:
        headers = {'X-User': _EMAIL, 'X-Profile': 'reader', 'Cookie': _GOOD_COOKIE}
        ws = await self.client.ws_connect('/ws', headers=headers)
        banner = await _read_until(ws, b'profile=reader')   # the pin is exported to the child
        self.assertIn(b'profile=reader', banner)
        await ws.close()


class PtySignalTest(unittest.TestCase):
    """The spawn bootstrap makes the slave the controlling terminal, so the
    line discipline turns a ^C byte into SIGINT — the property `pty.fork`
    gave us and the Popen path must preserve."""

    @staticmethod
    def _read_until(session: PtySession, buffer: bytes, needle: bytes,
                    timeout: float = 10.0) -> bytes:
        deadline = time.time() + timeout
        while needle not in buffer and time.time() < deadline:
            ready, _, _ = select.select([session.fd], [], [], 0.5)
            if ready:
                data = session.read()
                if not data:
                    break
                buffer += data
        return buffer

    def test_ctrl_c_reaches_the_shell(self) -> None:
        code = ('import signal, sys, time\n'
                "signal.signal(signal.SIGINT, lambda *a: print('CAUGHT-SIGINT', flush=True))\n"
                "print('READY', flush=True)\n"
                'time.sleep(30)\n')
        session = PtySession(ticket='unused', profile='', argv=(sys.executable, '-u', '-c', code))
        try:
            buffer = self._read_until(session, b'', b'READY')
            self.assertIn(b'READY', buffer)
            session.write(b'\x03')                        # ^C → SIGINT via the ctty
            buffer = self._read_until(session, buffer, b'CAUGHT-SIGINT')
            self.assertIn(b'CAUGHT-SIGINT', buffer)
        finally:
            session.close()
        self.assertFalse(session.is_alive())

    def test_the_shell_is_handed_its_osc_key(self) -> None:
        """The key the page will be given on attach is the one the shell's sequences carry."""
        code = "import os; print('KEY=' + os.environ.get('EULER_OSC_KEY', '') + '.', flush=True)"
        session = PtySession(ticket='unused', profile='', argv=(sys.executable, '-u', '-c', code))
        try:
            buffer = self._read_until(session, b'', b'.')
        finally:
            session.close()
        self.assertIn(f'KEY={session.osc_key}.'.encode(), buffer)
        self.assertRegex(session.osc_key, r'^[0-9a-f]{32}$')


class ReaperTests(_WsServiceCase):
    """The detached-TTL reaper (hygiene, not security): a shell nobody has reattached to for
    longer than the TTL is closed; an attached one never is."""

    detached_ttl = 1                          # reaper checks every ~1s (max(1, min(ttl, 60)))

    async def _shell_alive(self, email: str) -> bool:
        shells = self.app[PTY_MANAGER]._shells  # noqa: SLF001 — liveness probe
        return email in shells and shells[email].alive

    @unittest_run_loop
    async def test_detached_shell_is_reaped(self) -> None:
        ws = await self.client.ws_connect('/ws', headers=_HEADERS)
        await _read_until(ws, b'BANNER')
        session = self.app[PTY_MANAGER]._shells[_EMAIL].session  # noqa: SLF001
        await ws.close()                      # detach: the shell keeps running, idle clock starts

        for _ in range(80):                   # within a few reaper intervals it is gone
            if not await self._shell_alive(_EMAIL):
                break
            await asyncio.sleep(0.1)
        self.assertFalse(await self._shell_alive(_EMAIL), 'detached shell should be reaped')
        self.assertFalse(session.is_alive(), 'the PTY process should be terminated')

    @unittest_run_loop
    async def test_attached_shell_survives_the_reaper(self) -> None:
        ws = await self.client.ws_connect('/ws', headers=_HEADERS)
        await _read_until(ws, b'BANNER')
        await asyncio.sleep(2.5)              # several reaper intervals, socket still attached
        self.assertTrue(await self._shell_alive(_EMAIL), 'an attached shell must not be reaped')
        await ws.send_bytes(b'still-here\n')  # …and it still works
        self.assertIn(b'GOT:still-here', await _read_until(ws, b'GOT:still-here'))
        await ws.close()


class RealShellTest(_WsServiceCase):
    """Integration: fork the real `python -m euler_webshell.shell`; the child redeems the
    ticket against the fake auth socket (`EULER_AUTH_SOCKET`) and starts as
    the web-channel subject; `exit` ends it and the service closes the socket."""

    shell_argv: tuple[str, ...] = (sys.executable, '-m', 'euler_webshell.shell')

    @unittest_run_loop
    async def test_real_shell_attach_and_exit(self) -> None:
        os.environ['EULER_AUTH_SOCKET'] = str(self.auth_socket)   # inherited by the child
        self.addCleanup(os.environ.pop, 'EULER_AUTH_SOCKET', None)
        # …and point the child at a SCRATCH repo. A web-channel shell runs `git-sync` at
        # startup (packages/solver/solver/shell/shell.py), so without this the forked shell syncs whatever
        # checkout the suite happens to run in: stash → merge → pop over the operator's live
        # working tree, and — since `git-sync` repairs a locally-modified keys/enc-key.json —
        # a `git checkout HEAD --` over their uncommitted key material. It silently reverted
        # real key edits, on every test run and on every `git push`, because the pre-push
        # hook runs this suite. The sync fails in here (no remote) and the shell says so,
        # which is all this test needs it to do.
        scratch = TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        subprocess.run(['git', 'init', '-q'], cwd=scratch.name, check=False)
        os.environ['EULER_REPO_ROOT'] = scratch.name
        self.addCleanup(os.environ.pop, 'EULER_REPO_ROOT', None)

        ws = await self.client.ws_connect('/ws', headers=_HEADERS)
        await ws.send_str('{"resize": [120, 32]}')
        output = await _read_until(ws, b'SOLVER', timeout=60.0)   # the shell banner
        self.assertIn(b'SOLVER', output)                          # the shell came up
        self.assertEqual(self.auth.mints, 1)

        await ws.send_bytes(b'exit\n')
        await _read_close(ws, timeout=60.0)                       # shell exit → drainer → close


class TermModesTests(unittest.TestCase):
    """The terminal state a reattach restores, kept from the whole PTY stream — so a long
    session whose replay has lost the `busy` (or `claude`'s keyboard flags) still comes back
    with them."""

    KEY = 'ab' * 16

    def osc(self, state: str, key: str = KEY) -> bytes:
        return f'\x1b]5379;{key};{state};1700000000000\x07'.encode()

    def test_busy_outlives_the_replay_buffer(self) -> None:
        modes = TermModes(self.KEY)
        modes.feed(self.osc('busy'))
        modes.feed(b'x' * 1_000_000)                     # far past any replay cap
        self.assertTrue(modes.busy)
        modes.feed(self.osc('ready'))
        self.assertFalse(modes.busy)

    def test_a_sequence_split_across_reads_is_seen_once(self) -> None:
        seq = self.osc('busy') + b'\x1b[>1u'
        for cut in range(1, len(seq)):
            modes = TermModes(self.KEY)
            modes.feed(seq[:cut])
            modes.feed(seq[cut:])
            self.assertEqual((modes.busy, modes.kitty), (True, [0, 1]), cut)

    def test_printed_text_without_the_key_is_ignored(self) -> None:
        modes = TermModes(self.KEY)
        modes.feed(self.osc('busy', key='cd' * 16))
        self.assertFalse(modes.busy)

    def test_keyboard_modes_mirror_terminal_js(self) -> None:
        modes = TermModes(self.KEY)
        modes.feed(b'\x1b[>1u\x1b[=4;2u\x1b[>4;2m')
        self.assertEqual((modes.kitty, modes.other_keys), ([0, 5], 2))
        modes.feed(b'\x1b[=1;3u')                        # clear bits
        self.assertEqual(modes.kitty, [0, 4])
        modes.feed(b'\x1b[<5u\x1b[>m')                   # over-pop keeps the base; reset
        self.assertEqual((modes.kitty, modes.other_keys), ([0], 0))
        modes.feed(b'\x1b[>1u' * 100)                     # an app that never pops
        self.assertLessEqual(len(modes.kitty), 16)
        self.assertEqual(modes.snapshot(), {'busy': False, 'kitty': modes.kitty, 'otherKeys': 0,
                                            'mouse': 0, 'sgrMouse': False, 'focus': False,
                                            'paste': False})

    def test_reporting_modes_mirror_xterm(self) -> None:
        """The modes that make the terminal write to the PTY unasked — a stale focus mode
        types `ESC [ O` at the solver's prompt on every blur."""
        modes = TermModes(self.KEY)
        modes.feed(b'\x1b[?1004h\x1b[?1000;1006h\x1b[?2004h\x1b[?25l')   # 25: not followed
        self.assertEqual((modes.focus, modes.mouse, modes.sgr_mouse, modes.paste), (True, 1000, True, True))
        modes.feed(b'\x1b[?1003h')                       # one protocol at a time: the newest
        self.assertEqual(modes.mouse, 1003)
        modes.feed(b'\x1b[?1000l\x1b[?1004l')           # any protocol's reset turns tracking off
        self.assertEqual((modes.mouse, modes.focus), (0, False))
        modes.feed(b'\x1b[?1004h\x1bc')                 # RIS resets them all
        self.assertEqual((modes.focus, modes.sgr_mouse, modes.paste), (False, False, False))
        snap = modes.snapshot()
        self.assertEqual((snap['mouse'], snap['sgrMouse'], snap['focus'], snap['paste']), (0, False, False, False))


if __name__ == '__main__':
    unittest.main()

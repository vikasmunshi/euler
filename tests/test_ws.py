#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Tests for the web-shell service (Phase 6 step 1, DD-13/DD-14).

Covers the attach path end-to-end against a **fake auth service** on a unix
socket (real :class:`~solver.web.auth.tickets.TicketStore` semantics — mint
gated on the session cookie, redeem single-use): identity/pin refusals, the
ticket-then-fork flow, the binary/resize wire protocol, replay + shared attach
for a second tab, mint-refusal close, and the ``/internal/logout`` teardown
push. The PTY child is a stub echo shell so the suite stays fast; one
integration test forks the **real** ``python -m solver`` and drives it over the
ticket plane (the child redeems against the fake socket via
``EULER_AUTH_SOCKET``).
"""
from __future__ import annotations

import asyncio
import os
import select
import sys
import tempfile
import time
import unittest
from pathlib import Path

import aiohttp
from aiohttp import WSMsgType, web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from solver.auth.authorizations import DEFAULT_POLICY_FILE
from solver.web.auth.tickets import TicketStore
from solver.web.ws.app import PTY_MANAGER, build_app
from solver.web.ws.config import WsConfig
from solver.web.ws.pty import PtySession

_EMAIL = 'user@example.com'
_GOOD_COOKIE = 'solver_session=GOOD'
_HEADERS = {'X-User': _EMAIL, 'X-Profile': 'contributor', 'Cookie': _GOOD_COOKIE}

#: A minimal line-oriented stand-in for the solver shell: banner with the env it
#: received, echo with a marker, report its PTY size on demand, quit on 'exit'.
_STUB_CODE = """
import os, sys
print(f"BANNER ticket_len={len(os.environ.get('SOLVER_TICKET',''))} "
      f"profile={os.environ.get('EULER_PROFILE','')}", flush=True)
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


class _FakeAuth:
    """The auth service's shell-ticket surface, on a unix socket (DD-9 shape)."""

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

    async def get_application(self) -> web.Application:
        # Deterministic policy: the bundled ladder (reader/contributor/maintainer/admin).
        os.environ['EULER_AUTHZ_FILE'] = str(DEFAULT_POLICY_FILE)
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
                          shell_argv=self.shell_argv, detached_ttl=0)
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
        banner = await _read_until(ws, b'profile=contributor')
        self.assertIn(b'ticket_len=43', banner)          # token_urlsafe(32) → 43 chars
        self.assertEqual(self.auth.mints, 1)

        await ws.send_bytes(b'hello\n')
        self.assertIn(b'GOT:hello', await _read_until(ws, b'GOT:hello'))

        await ws.send_str('{"resize": [91, 33]}')
        await ws.send_bytes(b'size\n')
        self.assertIn(b'SIZE 91x33', await _read_until(ws, b'SIZE'))
        await ws.close()

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
    """The reader floor (DD-13): solver:execute is a reader grant — attach works."""

    profile = 'reader'

    @unittest_run_loop
    async def test_reader_attaches(self) -> None:
        headers = {'X-User': _EMAIL, 'X-Profile': 'reader', 'Cookie': _GOOD_COOKIE}
        ws = await self.client.ws_connect('/ws', headers=headers)
        banner = await _read_until(ws, b'profile=reader')  # the pin is exported to the child
        self.assertIn(b'profile=reader', banner)
        await ws.close()


class PtySignalTest(unittest.TestCase):
    """The spawn bootstrap makes the slave the controlling terminal, so the
    line discipline turns a ^C byte into SIGINT — the property ``pty.fork``
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


class RealShellTest(_WsServiceCase):
    """Integration: fork the real ``python -m solver``; the child redeems the
    ticket against the fake auth socket (``EULER_AUTH_SOCKET``) and starts as
    the web-channel subject; ``exit`` ends it and the service closes the socket."""

    shell_argv: tuple[str, ...] = (sys.executable, '-m', 'solver')

    @unittest_run_loop
    async def test_real_shell_attach_and_exit(self) -> None:
        os.environ['EULER_AUTH_SOCKET'] = str(self.auth_socket)   # inherited by the child
        self.addCleanup(os.environ.pop, 'EULER_AUTH_SOCKET', None)

        ws = await self.client.ws_connect('/ws', headers=_HEADERS)
        await ws.send_str('{"resize": [120, 32]}')
        output = await _read_until(ws, b'SOLVER', timeout=60.0)   # the shell banner
        self.assertIn(b'SOLVER', output)                          # the shell came up
        self.assertEqual(self.auth.mints, 1)

        await ws.send_bytes(b'exit\n')
        await _read_close(ws, timeout=60.0)                       # shell exit → drainer → close


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Tests for the per-user web service (MT-4): content + ``/ws`` folded onto one app.

Two surfaces on one application, sharing one per-user identity:

- **content** — the reused site routes gate on the request's Subject exactly as the
  standalone content service does; the new behaviour is the **per-user identity**: a
  request whose ``X-User`` maps to a slug other than this instance's ``EULER_USER_SLUG``
  is refused (misrouting/bypass), and an ``admin`` profile is served **uncapped** (MT-10a).
- **shell** — ``/ws`` attaches the browser terminal to this user's PTY shell against a
  **fake auth service** (real :class:`~solver.web.auth.tickets.TicketStore` semantics),
  with a stub echo shell so the suite stays fast; the child is pinned on the slug.
"""
from __future__ import annotations

import asyncio
import os
import sys
import tempfile
import unittest
from pathlib import Path

import aiohttp
from aiohttp import WSMsgType, web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from solver.auth.authorizations import DEFAULT_POLICY_FILE
from solver.auth.identity import system_slug
from solver.web.auth.tickets import TicketStore
from solver.web.user.app import PTY_MANAGER, build_app
from solver.web.user.config import UserConfig

_REPO_ROOT = Path(__file__).resolve().parents[1]
_EMAIL = 'me@example.com'
_SLUG = system_slug(_EMAIL)
_GOOD_COOKIE = 'solver_session=GOOD'
_OWN = {'X-User': _EMAIL, 'X-Profile': 'contributor'}
_OWN_WS = {**_OWN, 'Cookie': _GOOD_COOKIE}

#: Stub solver shell: banner echoing the env it received (the slug pin, not a profile).
_STUB_CODE = """
import os, sys
print(f"BANNER ticket_len={len(os.environ.get('SOLVER_TICKET',''))} "
      f"slug={os.environ.get('EULER_USER_SLUG','')} "
      f"profile_env={os.environ.get('EULER_PROFILE','-none-')} "
      f"auth_socket={os.environ.get('EULER_AUTH_SOCKET','')}", flush=True)
for line in sys.stdin:
    line = line.strip()
    if line == 'exit':
        break
    elif line:
        print('GOT:' + line, flush=True)
"""
_STUB_ARGV = (sys.executable, '-u', '-c', _STUB_CODE)


class _FakeAuth:
    """The auth service's shell-ticket surface on a unix socket (DD-9 shape)."""

    def __init__(self, email: str, profile: str) -> None:
        self.store = TicketStore()
        self.email, self.profile = email, profile
        self.mints = 0

    def build(self) -> web.Application:
        async def mint(request: web.Request) -> web.Response:
            if request.headers.get('Cookie', '') != _GOOD_COOKIE:
                return web.Response(status=401, text='no session')
            self.mints += 1
            return web.json_response({'ticket': self.store.mint(self.email, self.profile)})

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


class _UserServiceCase(AioHTTPTestCase):
    """Shared scaffolding: the fake auth socket + a slug-pinned per-user app."""

    email: str = _EMAIL
    profile: str = 'contributor'

    async def get_application(self) -> web.Application:
        os.environ['EULER_AUTHZ_FILE'] = str(DEFAULT_POLICY_FILE)
        self.addCleanup(os.environ.pop, 'EULER_AUTHZ_FILE', None)

        scratch = Path(tempfile.mkdtemp(prefix='euler-user-test-'))
        self.addCleanup(lambda: __import__('shutil').rmtree(scratch, True))
        self.auth = _FakeAuth(self.email, self.profile)
        self.auth_socket = scratch / 'auth.sock'
        self._auth_runner = web.AppRunner(self.auth.build())
        await self._auth_runner.setup()
        await web.UnixSite(self._auth_runner, str(self.auth_socket)).start()

        config = UserConfig(
            repo_root=_REPO_ROOT, static_dir=_REPO_ROOT / 'solver/web/content',
            socket_path=scratch / 'user.sock', socket_group='', tcp_bind='',
            serve_static=False, slug=_SLUG, auth_socket=str(self.auth_socket),
            shell_argv=_STUB_ARGV, detached_ttl=0)
        return build_app(config)

    async def tearDownAsync(self) -> None:
        await self._auth_runner.cleanup()
        await super().tearDownAsync()


class ContentIdentityTests(_UserServiceCase):
    """The per-user identity guard on the content surface."""

    @unittest_run_loop
    async def test_healthz_is_unauthenticated(self) -> None:
        self.assertEqual((await self.client.get('/healthz')).status, 200)

    @unittest_run_loop
    async def test_own_user_is_served(self) -> None:
        self.assertEqual((await self.client.get('/', headers=_OWN)).status, 200)

    @unittest_run_loop
    async def test_misrouted_user_is_refused(self) -> None:
        """A request for a DIFFERENT user reaching this instance = misrouting → 401."""
        resp = await self.client.get('/', headers={'X-User': 'someone@else.com', 'X-Profile': 'reader'})
        self.assertEqual(resp.status, 401)

    @unittest_run_loop
    async def test_admin_profile_is_not_capped(self) -> None:
        """MT-10a: admin is web-reachable — the account page (users:read) is served."""
        resp = await self.client.get('/account', headers={'X-User': _EMAIL, 'X-Profile': 'admin'})
        self.assertEqual(resp.status, 200)

    @unittest_run_loop
    async def test_no_forward_auth_headers_is_401(self) -> None:
        self.assertEqual((await self.client.get('/')).status, 401)

    @unittest_run_loop
    async def test_reader_cannot_reach_an_edit_route(self) -> None:
        resp = await self.client.get('/edit/solutions/0007/p0007_s0.py',
                                     headers={'X-User': _EMAIL, 'X-Profile': 'reader'})
        self.assertEqual(resp.status, 403)


class ShellAttachTests(_UserServiceCase):
    """``/ws`` on the same app: the attach gate, the slug pin, the wire, teardown."""

    @unittest_run_loop
    async def test_unauthenticated_ws_is_401(self) -> None:
        self.assertEqual((await self.client.get('/ws')).status, 401)

    @unittest_run_loop
    async def test_misrouted_ws_is_401(self) -> None:
        resp = await self.client.get('/ws', headers={'X-User': 'someone@else.com', 'X-Profile': 'reader'})
        self.assertEqual(resp.status, 401)

    @unittest_run_loop
    async def test_attach_pins_the_child_on_the_slug(self) -> None:
        ws = await self.client.ws_connect('/ws', headers=_OWN_WS)
        banner = await _read_until(ws, b'auth_socket=')
        self.assertIn(b'ticket_len=43', banner)                 # token_urlsafe(32) → 43 chars
        self.assertIn(f'slug={_SLUG}'.encode(), banner)         # the per-user pin (MT-4/MT-7)
        self.assertIn(b'profile_env=-none-', banner)            # no EULER_PROFILE in the per-user model
        self.assertIn(f'auth_socket={self.auth_socket}'.encode(), banner)
        self.assertEqual(self.auth.mints, 1)
        await ws.send_bytes(b'hi\n')
        self.assertIn(b'GOT:hi', await _read_until(ws, b'GOT:hi'))
        await ws.close()

    @unittest_run_loop
    async def test_internal_logout_reaps_the_shell(self) -> None:
        ws = await self.client.ws_connect('/ws', headers=_OWN_WS)
        await _read_until(ws, b'auth_socket=')
        self.assertIn(_EMAIL, self.app[PTY_MANAGER]._shells)     # noqa: SLF001 — liveness probe
        resp = await self.client.post('/internal/logout', json={'email': _EMAIL})
        self.assertEqual(resp.status, 200)
        self.assertTrue((await resp.json())['closed'])
        self.assertNotIn(_EMAIL, self.app[PTY_MANAGER]._shells)  # noqa: SLF001 — reaped
        await ws.close()


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The DD-14 teardown push: the auth service tears down a user's live web shell on
logout and on every revocation path, so a *running* shell's baked-in permissions die
at the event, not at the next login.

A fake ws instance (a unix socket exposing ``POST /internal/logout``, recording the
emails it is told to reap) stands in for the real ``euler-ws@<profile>`` sockets. The
real auth handlers are driven over TCP TestServers; the assertion is that the fake
socket received the teardown for the right email. The push is best-effort, so a second
test points the service at a missing socket and confirms the handler still succeeds."""
from __future__ import annotations

import secrets
import shutil
import tempfile
import unittest
from pathlib import Path

from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from solver.auth.identity import system_slug
from solver.web.auth.app import AuthService, build_admin_app, build_public_app
from solver.web.auth.config import AuthConfig
from solver.web.auth.policy import SESSION_COOKIE
from solver.web.auth.srp import compute_verifier

_EMAIL = 'shell-user@example.com'
_TOKEN = 'admin-token'


#: A deterministic policy for tests: the ladder plus an empty users map. Tests must
#: point EULER_AUTHZ_FILE at this — a host with the real /etc/euler SoR deployed would
#: otherwise leak its own user map into the run.
_AUTHZ_FIXTURE = Path(__file__).parent / 'fixtures' / 'authorizations.json'


class _FakeWsInstance:
    """Records the emails a teardown push targets (the user's own instance socket)."""

    def __init__(self) -> None:
        self.reaped: list[str] = []

    def build(self) -> web.Application:
        async def internal_logout(request: web.Request) -> web.Response:
            body = await request.json()
            self.reaped.append(str(body.get('email', '')))
            return web.json_response({'closed': True})

        app = web.Application()
        app.add_routes([web.post('/internal/logout', internal_logout)])
        return app


class TeardownPushTests(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        import os
        os.environ['EULER_AUTHZ_FILE'] = str(_AUTHZ_FIXTURE)
        self.addCleanup(os.environ.pop, 'EULER_AUTHZ_FILE', None)

        self.scratch = Path(tempfile.mkdtemp(prefix='euler-teardown-'))
        self.addCleanup(shutil.rmtree, self.scratch, True)

        # The fake instance on the user's own socket (user-<slug>.sock), where the real
        # per-user instance would be (MT-4).
        self.ws = _FakeWsInstance()
        self.ws_socket = self.scratch / f'user-{system_slug(_EMAIL)}.sock'
        self._ws_runner = web.AppRunner(self.ws.build())
        await self._ws_runner.setup()
        await web.UnixSite(self._ws_runner, str(self.ws_socket)).start()
        self.addAsyncCleanup(self._ws_runner.cleanup)

        # The teardown push derives the target socket (user-<slug>.sock) from this dir.
        config = AuthConfig(
            state_dir=self.scratch, socket_path=self.scratch / 'auth.sock',
            admin_socket_path=self.scratch / 'admin.sock', socket_group='',
            admin_socket_group='', admin_token=_TOKEN, base_url='https://example.test',
            smtp_relay='127.0.0.1:25', terms_version='test',
            user_socket_dir=str(self.scratch))
        self.service = AuthService(config)

        salt = secrets.token_bytes(16)
        self.service.users.create(_EMAIL, salt.hex(),
                                  f'{compute_verifier(salt, _EMAIL, "pw"):x}', 'test', 'now')

        self.public = TestClient(TestServer(build_public_app(self.service)))
        self.admin = TestClient(TestServer(build_admin_app(self.service)))
        await self.public.start_server()
        await self.admin.start_server()
        self.addAsyncCleanup(self.public.close)
        self.addAsyncCleanup(self.admin.close)

    def _session_cookie(self) -> dict[str, str]:
        token = self.service.sessions.create(_EMAIL, 'contributor')
        return {SESSION_COOKIE: token}

    async def test_logout_pushes_teardown(self) -> None:
        self.public.session.cookie_jar.update_cookies(self._session_cookie())
        resp = await self.public.post('/auth/logout')
        self.assertEqual(resp.status, 200)
        self.assertEqual(self.ws.reaped, [_EMAIL])          # only the live socket, no crash on the absent one

    async def test_disable_pushes_teardown(self) -> None:
        resp = await self.admin.post(f'/admin/users/{_EMAIL}/disable',
                                     headers={'X-Admin-Token': _TOKEN})
        self.assertEqual(resp.status, 200)
        self.assertEqual(self.ws.reaped, [_EMAIL])

    async def test_remove_pushes_teardown(self) -> None:
        resp = await self.admin.delete(f'/admin/users/{_EMAIL}',
                                       headers={'X-Admin-Token': _TOKEN})
        self.assertEqual(resp.status, 200)
        self.assertEqual(self.ws.reaped, [_EMAIL])

    async def test_users_change_revoke_pushes_teardown(self) -> None:
        """The `users change` path: the admin CLI rewrites the map then calls
        /admin/users/{email}/revoke, which must also reap the live shell (DD-14)."""
        resp = await self.admin.post(f'/admin/users/{_EMAIL}/revoke',
                                     headers={'X-Admin-Token': _TOKEN})
        self.assertEqual(resp.status, 200)
        self.assertEqual(self.ws.reaped, [_EMAIL])

    async def test_enable_does_not_push(self) -> None:
        """Enabling an account is not a revocation — no teardown."""
        resp = await self.admin.post(f'/admin/users/{_EMAIL}/enable',
                                     headers={'X-Admin-Token': _TOKEN})
        self.assertEqual(resp.status, 200)
        self.assertEqual(self.ws.reaped, [])

    async def test_push_is_best_effort_when_the_socket_is_absent(self) -> None:
        """With no reachable instance socket, a revocation still succeeds (the push
        swallows the connection failure) — the shell simply isn't there to reap."""
        self.ws_socket.unlink()                              # kill the user's socket
        await self._ws_runner.cleanup()
        resp = await self.admin.post(f'/admin/users/{_EMAIL}/revoke',
                                     headers={'X-Admin-Token': _TOKEN})
        self.assertEqual(resp.status, 200)
        self.assertEqual(self.ws.reaped, [])


if __name__ == '__main__':
    unittest.main()

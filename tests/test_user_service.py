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
from solver.crypto import vault
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
      f"auth_socket={os.environ.get('EULER_AUTH_SOCKET','')} "
      f"vk_file={os.environ.get('EULER_VAULT_KEY_FILE','-none-')}", flush=True)
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


class VaultRouteTests(_UserServiceCase):
    """The vault + account surface (MT-6/MT-8): unlock/init, rewrap, secrets, reset."""

    _SALT = bytes(range(16))

    async def get_application(self) -> web.Application:
        from solver.crypto.config import config as crypto_config
        from solver.web.user import vault_api

        secrets = Path(tempfile.mkdtemp(prefix='euler-vault-test-'))
        self.addCleanup(lambda: __import__('shutil').rmtree(secrets, True))
        self._saved = {k: crypto_config[k] for k in
                       ('private_key_file', 'env_file', 'vault_file', 'user_pass_file',
                        'vault_kdf_iterations')}
        crypto_config['private_key_file'] = secrets / 'id'
        crypto_config['env_file'] = secrets / 'env'
        crypto_config['vault_file'] = secrets / 'vault'
        crypto_config['user_pass_file'] = secrets / 'user_pass'
        crypto_config['vault_kdf_iterations'] = 1000

        def _restore() -> None:
            crypto_config.update(self._saved)   # type: ignore[typeddict-item]
            vault.clear_session_key()

        self.addCleanup(_restore)
        vault.clear_session_key()
        # The gh / Claude Code probes shell out; keep the suite hermetic.
        self._saved_probes = (vault_api._tool_status, vault_api._claude_status)  # noqa: SLF001
        vault_api._tool_status = lambda *a, **k: 'not installed'  # type: ignore[assignment]
        vault_api._claude_status = lambda: 'not installed'        # type: ignore[assignment]
        self.addCleanup(lambda: (setattr(vault_api, '_tool_status', self._saved_probes[0]),
                                 setattr(vault_api, '_claude_status', self._saved_probes[1])))
        self.env_file = secrets / 'env'
        return await super().get_application()

    def _pk(self, password: str, salt: bytes | None = None) -> str:
        return vault.derive_password_key(password, salt or self._SALT, 1000).hex()

    async def _unlock(self, password: str = 'pw') -> aiohttp.ClientResponse:
        return await self.client.post('/vault/unlock', headers=_OWN, json={
            'pk': self._pk(password), 'salt': self._SALT.hex()})

    @unittest_run_loop
    async def test_vault_routes_require_identity(self) -> None:
        for method, path in (('GET', '/vault/status'), ('POST', '/vault/unlock'),
                             ('POST', '/vault/rewrap'), ('GET', '/account/vault'),
                             ('POST', '/account/secret')):
            resp = await self.client.request(method, path)
            self.assertEqual(resp.status, 401, path)

    @unittest_run_loop
    async def test_first_login_initialises_and_unlocks(self) -> None:
        status = await (await self.client.get('/vault/status', headers=_OWN)).json()
        self.assertEqual(status, {'vault': False, 'unlocked': False})
        resp = await self._unlock()
        self.assertEqual(resp.status, 200)
        self.assertEqual(await resp.json(), {'unlocked': True, 'initialized': True})
        status = await (await self.client.get('/vault/status', headers=_OWN)).json()
        self.assertTrue(status['vault'] and status['unlocked'])
        self.assertEqual(status['salt'], self._SALT.hex())
        self.assertTrue(vault.vault_exists())

    @unittest_run_loop
    async def test_wrong_pk_is_stale_never_destructive(self) -> None:
        vault.init_vault_from_pk(bytes.fromhex(self._pk('right')), self._SALT)
        resp = await self._unlock('wrong')
        self.assertEqual(resp.status, 409)
        self.assertTrue((await resp.json())['stale'])
        self.assertTrue(vault.vault_exists())               # untouched
        self.assertEqual((await self._unlock('right')).status, 200)

    @unittest_run_loop
    async def test_rewrap_carries_the_vault_across_a_password_change(self) -> None:
        vk = vault.init_vault_from_pk(bytes.fromhex(self._pk('old')), self._SALT)
        new_salt = bytes(range(16, 32))
        resp = await self.client.post('/vault/rewrap', headers=_OWN, json={
            'old_pk': self._pk('old'), 'new_pk': self._pk('new', new_salt),
            'new_salt': new_salt.hex()})
        self.assertEqual(resp.status, 200)
        self.assertEqual(vault.unlock_vault_with_pk(bytes.fromhex(self._pk('new', new_salt))), vk)
        with self.assertRaises(Exception):                  # the old wrap is gone
            vault.unlock_vault_with_pk(bytes.fromhex(self._pk('old')))

    @unittest_run_loop
    async def test_secret_upsert_and_delete_are_write_only(self) -> None:
        await self._unlock()
        resp = await self.client.post('/account/secret', headers=_OWN, data={
            'name': 'ANTHROPIC_API_KEY', 'value': 'sk-super-secret'})
        self.assertEqual(resp.status, 200)
        page = await resp.text()
        self.assertIn('<code>ANTHROPIC_API_KEY</code>', page)   # the NAME is listed…
        self.assertNotIn('sk-super-secret', page)               # …the VALUE is never rendered
        self.assertTrue(vault.is_vault_encrypted(self.env_file.read_bytes()))
        resp = await self.client.post('/account/secret/delete', headers=_OWN,
                                      data={'name': 'ANTHROPIC_API_KEY'})
        self.assertEqual(resp.status, 200)
        self.assertNotIn('<code>ANTHROPIC_API_KEY</code>', await resp.text())

    @unittest_run_loop
    async def test_secret_upsert_locked_is_409_and_bad_name_400(self) -> None:
        resp = await self.client.post('/account/secret', headers=_OWN,
                                      data={'name': 'X_KEY', 'value': 'v'})
        self.assertEqual(resp.status, 409)                  # no vault / locked
        await self._unlock()
        resp = await self.client.post('/account/secret', headers=_OWN,
                                      data={'name': 'bad name!', 'value': 'v'})
        self.assertEqual(resp.status, 400)

    @unittest_run_loop
    async def test_internal_vault_reset_destroys_the_vault(self) -> None:
        await self._unlock()
        await self.client.post('/account/secret', headers=_OWN,
                               data={'name': 'A_KEY', 'value': 'v'})
        resp = await self.client.post('/internal/vault-reset', json={'email': _EMAIL})
        self.assertEqual(resp.status, 200)
        removed = (await resp.json())['removed']
        self.assertIn('vault', removed)
        self.assertIn('env', removed)
        self.assertFalse(vault.vault_exists())
        self.assertIsNone(vault.session_vault_key())        # locked out too

    @unittest_run_loop
    async def test_shell_forked_after_unlock_inherits_the_session_key(self) -> None:
        """The MT-12 delivery through the web path: unlock, then attach — the child
        finds the uid-private key file by inherited environment and can read VK."""
        await self._unlock()
        ws = await self.client.ws_connect('/ws', headers=_OWN_WS)
        banner = await _read_until(ws, b'vk_file=')
        vk_path = banner.split(b'vk_file=')[1].split()[0].decode()
        self.assertNotEqual(vk_path, '-none-')
        self.assertEqual(len(Path(vk_path).read_bytes()), 32)   # the actual VK, 0600 tmpfs
        await ws.close()

    @unittest_run_loop
    async def test_malformed_pk_is_400(self) -> None:
        resp = await self.client.post('/vault/unlock', headers=_OWN,
                                      json={'pk': 'zz', 'salt': self._SALT.hex()})
        self.assertEqual(resp.status, 400)


if __name__ == '__main__':
    unittest.main()

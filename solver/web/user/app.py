#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The per-user aiohttp app: one collaborator's content **and** web shell.

``build_app`` folds two surfaces onto one application:

- **content** — the whole site route table, reused verbatim from
  :func:`solver.web.site.app.install_content` (home, solutions, docs, topics,
  account, the edit routes). Nothing about those handlers is per-profile; they read
  the request's :class:`~solver.auth.subject.Subject` and gate on it.
- **shell** — ``GET /ws`` attaches the browser terminal to *this user's* persistent
  PTY shell (:mod:`solver.web.ws` machinery), and ``POST /internal/logout`` is the
  auth service's teardown push (socket-peer only; Caddy never routes it).

The difference from the retired per-profile services is **identity**: this process
*is* one user's uid (``EULER_USER_SLUG``), so the identity middleware refuses any
request whose ``X-User`` maps to a different slug — misrouting or a bypass — and it
resolves the profile from the trusted ``X-Profile`` uncapped (an ``admin`` account is
web-reachable now). Caddy routes every request to the right user's socket by
``X-User-Slug``, so in production the pin only ever agrees; the check is the
code-side backstop to that OS boundary.
"""
from __future__ import annotations

__all__ = ['build_app', 'PTY_MANAGER']

import asyncio
import json
import logging
from typing import Any, Awaitable, Callable

from aiohttp import WSCloseCode, WSMsgType, web

from solver.auth import Authorizations, Subject
from solver.auth.identity import system_slug
from solver.crypto import vault
from solver.web.auth.client import request as auth_request
from solver.web.cache import cache_middleware
from solver.web.csp import csp_middleware
from solver.web.site.app import _MAX_BODY, install_content
from solver.web.site.render import SUBJECT_KEY
from solver.web.user.config import UserConfig
from solver.web.user.vault_api import add_vault_routes
from solver.web.ws.manager import PtyManager
from solver.web.ws.pty import PtySession

log = logging.getLogger('euler-user')

_Handler = Callable[[web.Request], Awaitable[web.StreamResponse]]

#: The attach gate: the reader-floor "may run the solver at all" grant.
ATTACH_REQUIRES: str = 'reader'

#: Per-app PtyManager, for tests and the lifecycle hooks.
PTY_MANAGER: web.AppKey[PtyManager] = web.AppKey('pty_manager', PtyManager)
#: The detached-TTL reaper task, stored so cleanup can cancel it.
_REAPER_TASK: web.AppKey[asyncio.Task[None]] = web.AppKey('reaper_task', asyncio.Task)


def _subject_from_headers(request: web.Request, authz: Authorizations,
                          pin_slug: str) -> Subject | None:
    """Build the request's Subject from the forward_auth headers, or None.

    Caddy guarantees ``X-User``/``X-Profile`` on every routed request and strips any
    client copy. A missing/unknown profile yields None. *pin_slug* is this
    instance's own user (``EULER_USER_SLUG``): a request whose ``X-User`` maps to a
    different :func:`system_slug` is refused (None) — Caddy routes each user to their
    own socket, so a mismatch means misrouting or a bypass. The profile is **not**
    capped: an ``admin`` account is web-reachable.
    """
    user = request.headers.get('X-User', '').strip()
    profile = request.headers.get('X-Profile', '').strip()
    if not user or not profile or profile not in authz.known_profiles():
        return None
    if pin_slug and system_slug(user) != pin_slug:
        return None
    return Subject(user=user, slug=system_slug(user), channel='web',
                   auth_method='forward-auth', profile=profile)


def _parse_resize(raw: str) -> tuple[int, int] | None:
    """Parse a ``{"resize": [cols, rows]}`` control frame; None if it is not one."""
    try:
        message = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(message, dict):
        return None
    size = message.get('resize')
    if (isinstance(size, list) and len(size) == 2
            and all(isinstance(v, int) and 0 < v < 1000 for v in size)):
        return size[0], size[1]
    return None


def build_app(config: UserConfig) -> web.Application:
    """Assemble the per-user app: content + ``/ws`` on one application."""
    authz = Authorizations.load()
    pin_slug = config.slug
    manager = PtyManager()

    @web.middleware
    async def identity_middleware(request: web.Request, handler: _Handler) -> web.StreamResponse:
        request[SUBJECT_KEY] = _subject_from_headers(request, authz, pin_slug)
        return await handler(request)

    app = web.Application(middlewares=[cache_middleware, csp_middleware, identity_middleware],
                          client_max_size=_MAX_BODY)
    # The content surface (routes + jinja + static + /healthz) — reused verbatim.
    install_content(app, config.site_config(), authz)
    # The vault + account surface — this instance IS the user's uid.
    add_vault_routes(app)
    app[PTY_MANAGER] = manager

    async def _mint_ticket(cookie: str) -> str:
        """Mint a one-time shell ticket against the caller's live session.

        The auth client is blocking stdlib; run it off-loop. Any refusal aborts the
        fork — an unvouched shell must not start.
        """
        loop = asyncio.get_running_loop()
        try:
            status, data = await loop.run_in_executor(
                None, lambda: auth_request(config.auth_socket, 'POST', '/shell-ticket',
                                           headers={'Cookie': cookie}))
        except OSError as exc:
            raise PermissionError(f'auth service unreachable ({exc})') from None
        if status != 200 or not isinstance(data, dict) or not data.get('ticket'):
            raise PermissionError('shell ticket refused')
        return str(data['ticket'])

    async def websocket(request: web.Request) -> web.StreamResponse:
        """Attach a browser terminal to this user's persistent shell."""
        subject: Subject | None = request.get(SUBJECT_KEY)
        if subject is None:
            return web.Response(status=401, text='unauthenticated')
        if not subject.has(ATTACH_REQUIRES):
            return web.Response(status=403, text='forbidden')

        ws = web.WebSocketResponse(heartbeat=30.0)
        await ws.prepare(request)
        cookie = request.headers.get('Cookie', '')

        async def spawn() -> PtySession:
            ticket = await _mint_ticket(cookie)
            # The child pins on this instance's slug (EULER_USER_SLUG); its profile comes
            # from redeeming the ticket, not from us.
            return PtySession(ticket=ticket, argv=config.shell_argv,
                              auth_socket=config.auth_socket, slug=config.slug)

        try:
            pty = await manager.get_or_create(subject.user, spawn)
        except PermissionError as exc:
            log.warning('attach refused for %s: %s', subject.user, exc)
            await ws.close(code=WSCloseCode.POLICY_VIOLATION, message=str(exc).encode())
            return ws
        log.info('%s attached (profile %s)', subject.user, subject.profile)

        await pty.attach(ws)
        try:
            async for msg in ws:
                if msg.type == WSMsgType.BINARY:
                    pty.write(msg.data)
                elif msg.type == WSMsgType.TEXT:
                    size = _parse_resize(msg.data)
                    if size is not None:
                        pty.resize(cols=size[0], rows=size[1])
                elif msg.type == WSMsgType.ERROR:
                    break
        finally:
            pty.detach(ws)  # the shell keeps running; only this socket goes away
            log.info('%s detached', subject.user)
        return ws

    async def internal_logout(request: web.Request) -> web.Response:
        """Tear down this user's shell on the auth service's push.

        Reachable only by socket peers (``euler-web`` members) — Caddy never routes
        here. Idempotent: closing an absent shell reports closed=False.
        """
        try:
            body: Any = await request.json()
        except json.JSONDecodeError:
            return web.Response(status=400, text='bad request')
        email = str(body.get('email', '')).strip() if isinstance(body, dict) else ''
        if not email:
            return web.Response(status=400, text='bad request')
        closed = await manager.close(email)
        vault.clear_session_key()       # the session ended — leave no reachable key material
        log.info('logout push for %s (shell %s)', email, 'closed' if closed else 'absent')
        return web.json_response({'closed': closed})

    async def _reaper() -> None:
        """Reap shells detached longer than the TTL (hygiene, not security). Never dies."""
        ttl = config.detached_ttl
        interval = max(1, min(ttl, 60))
        while True:
            await asyncio.sleep(interval)
            try:
                for email in await manager.reap_detached(ttl):
                    log.info('reaped detached shell for %s (idle > %ds)', email, ttl)
            except Exception:                # noqa: BLE001 — the reaper must keep running
                log.exception('reaper pass failed')

    async def _on_startup(app_: web.Application) -> None:
        if config.detached_ttl > 0:
            app_[_REAPER_TASK] = asyncio.create_task(_reaper())

    async def _cancel_reaper(app_: web.Application) -> None:
        task = app_.get(_REAPER_TASK)
        if task is not None:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    async def _close_all(app_: web.Application) -> None:
        await app_[PTY_MANAGER].close_all()
        vault.clear_session_key()       # service stop: drop the tmpfs key file too

    app.add_routes([
        web.get('/ws', websocket),
        web.post('/internal/logout', internal_logout),
    ])
    app.on_startup.append(_on_startup)
    app.on_cleanup.append(_cancel_reaper)
    app.on_cleanup.append(_close_all)
    return app

#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The web-shell aiohttp app: identity from forward_auth, the /ws attach, teardown.

Three routes:

- ``GET /healthz`` — the kit's socket probe.
- ``GET /ws`` — attach the browser terminal to the caller's persistent shell.
  Identity is the trusted ``X-User``/``X-Profile`` pair (Caddy strips
  client-supplied copies and stamps the ``forward_auth`` response); the
  instance refuses a profile that differs from its ``EULER_PROFILE`` pin and
  gates attach on the **reader floor**. On fork it forwards the caller's
  session cookie to the auth service's ``POST /shell-ticket`` and passes only
  the minted single-use ticket to the child.
- ``POST /internal/logout`` — the auth service's teardown push:
  ``{"email": …}`` closes that user's shell. Socket-peer only — Caddy routes
  ``/ws`` and nothing else to this service, so no browser can reach it.

Wire protocol on ``/ws``: binary frames are raw PTY bytes both ways; a text
frame ``{"resize": [cols, rows]}`` propagates the browser geometry.
"""
from __future__ import annotations

__all__ = ['build_app']

import asyncio
import json
import logging
from typing import Any

from aiohttp import WSCloseCode, WSMsgType, web

from solver.auth.authorizations import Authorizations
from solver.auth.identity import slugify
from solver.auth.subject import Subject
from solver.web.auth.client import request as auth_request
from solver.web.ws.config import WsConfig
from solver.web.ws.manager import PtyManager
from solver.web.ws.pty import PtySession

log = logging.getLogger('euler-ws')

#: The attach gate: the reader-floor "may run the solver at all" grant.
ATTACH_REQUIRES: str = 'reader'

#: Per-app PtyManager, for tests and the lifecycle hooks.
PTY_MANAGER: web.AppKey[PtyManager] = web.AppKey('pty_manager', PtyManager)
#: The detached-TTL reaper task, stored so cleanup can cancel it.
_REAPER_TASK: web.AppKey[asyncio.Task[None]] = web.AppKey('reaper_task', asyncio.Task)


def _subject_from_headers(request: web.Request, authz: Authorizations,
                          pin: str) -> Subject | None:
    """Build the request's Subject from the forward_auth headers, or None.

    Caddy guarantees these headers on every routed request (and strips any
    client-supplied copies). A missing/unknown profile yields None; so
    does a profile differing from this instance's *pin* — Caddy routes each
    profile to its own per-profile uid's socket, so a mismatch means misrouting
    or a bypass (the code-side backstop to the OS boundary).
    """
    user = request.headers.get('X-User', '').strip()
    profile = request.headers.get('X-Profile', '').strip()
    if not user or not profile or profile not in authz.known_profiles():
        return None
    if pin and profile != pin:
        return None
    return Subject(user=user, slug=slugify(user), channel='web',
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


def build_app(config: WsConfig) -> web.Application:
    """Assemble the web-shell app for one per-profile instance."""
    authz = Authorizations.load()
    manager = PtyManager()

    async def _mint_ticket(cookie: str) -> str:
        """Mint a one-time shell ticket against the caller's live session.

        The auth client is blocking stdlib; run it off-loop. Any refusal —
        session died between forward_auth and here, service down — aborts the
        fork: an unvouched shell must not start.
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

    async def healthz(request: web.Request) -> web.Response:
        return web.Response(text='ok')

    async def websocket(request: web.Request) -> web.StreamResponse:
        """Attach a browser terminal to the signed-in user's persistent shell.

        The shell is forked on first attach (minting the ticket then), replayed
        on reattach; binary frames are keystrokes, a `resize` text frame drives
        the shared PTY geometry. Detach leaves the shell running.
        """
        subject = _subject_from_headers(request, authz, config.profile)
        if subject is None:
            return web.Response(status=401, text='unauthenticated')
        if not subject.has(ATTACH_REQUIRES):
            return web.Response(status=403, text='forbidden')

        ws = web.WebSocketResponse(heartbeat=30.0)
        await ws.prepare(request)

        cookie = request.headers.get('Cookie', '')

        async def spawn() -> PtySession:
            ticket = await _mint_ticket(cookie)
            return PtySession(ticket=ticket, profile=config.profile or subject.profile,
                              argv=config.shell_argv, auth_socket=config.auth_socket)

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
        """Tear down a user's shell on the auth service's push.

        Reachable only by socket peers (`euler-web` members) — Caddy never
        routes here. Idempotent: closing an absent shell reports closed=False.
        """
        try:
            body: Any = await request.json()
        except json.JSONDecodeError:
            return web.Response(status=400, text='bad request')
        email = str(body.get('email', '')).strip() if isinstance(body, dict) else ''
        if not email:
            return web.Response(status=400, text='bad request')
        closed = await manager.close(email)
        log.info('logout push for %s (shell %s)', email, 'closed' if closed else 'absent')
        return web.json_response({'closed': closed})

    async def _close_all(app: web.Application) -> None:
        await app[PTY_MANAGER].close_all()

    async def _reaper() -> None:
        """Periodically reap shells detached longer than the TTL (hygiene, not security).

        The cadence tracks the TTL (a short test TTL is checked often; the 24 h
        production default every 60 s), so a shell is reaped within one interval of
        crossing it. A reaper failure must not take the loop down.
        """
        ttl = config.detached_ttl
        interval = max(1, min(ttl, 60))
        while True:
            await asyncio.sleep(interval)
            try:
                for email in await manager.reap_detached(ttl):
                    log.info('reaped detached shell for %s (idle > %ds)', email, ttl)
            except Exception:                # noqa: BLE001 — the reaper must keep running
                log.exception('reaper pass failed')

    async def _on_startup(app: web.Application) -> None:
        if config.detached_ttl > 0:
            app[_REAPER_TASK] = asyncio.create_task(_reaper())

    async def _cancel_reaper(app: web.Application) -> None:
        task = app.get(_REAPER_TASK)
        if task is not None:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    app = web.Application()
    app[PTY_MANAGER] = manager
    app.add_routes([
        web.get('/healthz', healthz),
        web.get('/ws', websocket),
        web.post('/internal/logout', internal_logout),
    ])
    app.on_startup.append(_on_startup)
    app.on_cleanup.append(_cancel_reaper)
    app.on_cleanup.append(_close_all)
    return app

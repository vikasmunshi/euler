#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The content service aiohttp app: identity from forward_auth, routes, gating.

``build_app`` wires the shared CSP middleware (:mod:`solver.web.csp`) and an
**identity middleware** that turns Caddy's trusted ``X-User`` / ``X-Profile``
(set by ``forward_auth``; client-supplied copies are stripped at the edge, §4.1)
into a :class:`~solver.auth.subject.Subject`. Routes gate on it with
:func:`requires`, the web counterpart of the shell's ``@register(requires=…)``
(DD-12): the same ``object:permission`` grants, checked against ``X-Profile``.

Phase 5a serves the home/navigation shell and a placeholder panel standing in
for the web shell (Phase 6), establishing the full-page-vs-block contract
(:mod:`solver.web.site.render`). Later sub-steps add the view (5b) and edit
(5c/5d) routes on the same spine.
"""
from __future__ import annotations

__all__ = ['build_app']

import logging
from pathlib import Path
from typing import Awaitable, Callable

import aiohttp_jinja2
import jinja2
from aiohttp import web

from solver.auth import Authorizations, Subject, slugify
from solver.web.csp import csp_middleware
from solver.web.site.config import SiteConfig
from solver.web.site.render import SUBJECT_KEY, render

log = logging.getLogger('euler-content')

_TEMPLATES = Path(__file__).resolve().parent / 'templates'
_Handler = Callable[[web.Request], Awaitable[web.StreamResponse]]

#: The capability every authenticated profile holds — "may view the site".
VIEW = 'web-content:read'


def _subject_from_headers(request: web.Request, authz: Authorizations,
                          pin: str = '') -> Subject | None:
    """Build the request's Subject from the forward_auth headers, or None.

    Caddy guarantees these headers on every routed request (and strips any
    client-supplied copies). A missing/unknown profile yields None — the
    identity middleware then answers 401, since only Caddy should reach us.

    *pin* is this instance's own profile (``EULER_PROFILE``, DD-12): when set, a
    request whose ``X-Profile`` differs is refused (None). Caddy routes each
    profile to its own per-profile uid's socket, so a mismatch means misrouting
    or a bypass — the code-side backstop to the OS per-profile boundary.
    """
    user = request.headers.get('X-User', '').strip()
    profile = request.headers.get('X-Profile', '').strip()
    if not profile or profile not in authz.known_profiles():
        return None
    if pin and profile != pin:
        return None
    return Subject(user=user, slug=slugify(user or profile), channel='web',
                   auth_method='forward-auth', profile=profile,
                   permissions=authz.permissions_for(profile))


def requires(capability: str) -> Callable[[_Handler], _Handler]:
    """Gate a handler on *capability* against the request's Subject (DD-12).

    401 when there is no subject (an unauthenticated caller that bypassed Caddy);
    403 when the subject lacks the grant. Mirrors the shell decorator's contract.
    """

    def _wrap(handler: _Handler) -> _Handler:
        async def _guarded(request: web.Request) -> web.StreamResponse:
            subject: Subject | None = request.get(SUBJECT_KEY)
            if subject is None:
                raise web.HTTPUnauthorized(text='authentication required')
            if not subject.has(capability):
                raise web.HTTPForbidden(text=f'requires {capability}')
            return await handler(request)

        return _guarded

    return _wrap


# ── handlers ────────────────────────────────────────────────────────────────────────

async def healthz(request: web.Request) -> web.Response:
    """Liveness probe (unauthenticated) — Caddy/monitoring only."""
    return web.Response(text='ok')


@requires(VIEW)
async def home(request: web.Request) -> web.StreamResponse:
    """The landing page: welcome + navigation. Full page, or its ``main`` block."""
    return render(request, 'home.html', block='main')


@requires(VIEW)
async def shell_panel(request: web.Request) -> web.StreamResponse:
    """The placeholder web-shell panel (Phase 6 stands in here) — full page or block."""
    return render(request, 'shell.html', block='main')


# ── app wiring ────────────────────────────────────────────────────────────────────────

def build_app(config: SiteConfig) -> web.Application:
    """Build the content-service application for one process."""
    authz = Authorizations.load()
    pin = config.profile

    @web.middleware
    async def identity_middleware(request: web.Request, handler: _Handler) -> web.StreamResponse:
        request[SUBJECT_KEY] = _subject_from_headers(request, authz, pin)
        return await handler(request)

    app = web.Application(middlewares=[csp_middleware, identity_middleware])
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(str(_TEMPLATES)),
                         autoescape=jinja2.select_autoescape(['html', 'xml']))
    app.add_routes([
        web.get('/healthz', healthz),
        web.get('/', home),
        web.get('/shell', shell_panel),
    ])
    if config.serve_static:
        # Dev only — in production Caddy serves these from /etc/euler/web-content.
        app.router.add_static('/assets', config.static_dir / 'assets')
        app.router.add_static('/vendor', config.static_dir / 'vendor')
    return app

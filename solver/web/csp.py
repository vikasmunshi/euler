#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Content-Security-Policy middleware with a per-response nonce (shared).

Every page an app service renders carries the locked baseline CSP
(docs/web-server-guide.md § Content-Security-Policy): same-origin everything,
no ``unsafe-inline``, no ``unsafe-eval``, no framing. The middleware mints a
fresh nonce per response and exposes it as ``request['csp_nonce']`` so a
template *can* mark an unavoidable inline ``<script>``/``<style>`` — the auth
pages don't need it (all their JS/CSS is served from ``/assets``), but the
contract is established here once and every rendering service imports the same
middleware.

Caddy adds the transport-level headers (HSTS, ``X-Content-Type-Options``, …)
and a fallback CSP for purely static responses; this header wins on rendered
pages because the app sets it per response.
"""
from __future__ import annotations

__all__ = ['csp_middleware', 'NONCE_KEY']

import secrets
from typing import Any, Awaitable, Callable

from aiohttp import web

#: Request key under which the per-response nonce is exposed to handlers/templates.
NONCE_KEY: str = 'csp_nonce'

#: ``style-src`` carries ``'unsafe-inline'`` for exactly one consumer: MathJax
#: (and htmx's indicator rules) inject their stylesheets at runtime with no
#: nonce hook — verified blocked under bare ``'self'`` (headless-Chrome CSP
#: violations, garbled math). Scripts stay strict: ``'self'`` + nonce only.
#: ``frame-ancestors 'self'`` (not ``'none'``): the app shell frames its own
#: ``/terminal`` document — cross-origin embedding stays blocked. See
#: docs/web-server-guide.md § Content-Security-Policy for the recorded trade-offs.
_POLICY = ("default-src 'self'; "
           "script-src 'self' 'nonce-{nonce}'; "
           "style-src 'self' 'unsafe-inline'; "
           "img-src 'self' data:; "
           "connect-src 'self'; "
           "frame-ancestors 'self'; "
           "base-uri 'none'; "
           "object-src 'none'")

_Handler = Callable[[web.Request], Awaitable[web.StreamResponse]]


@web.middleware
async def csp_middleware(request: web.Request, handler: _Handler) -> web.StreamResponse:
    """Mint ``request['csp_nonce']`` and stamp the baseline CSP on the response."""
    nonce = secrets.token_urlsafe(16)
    request[NONCE_KEY] = nonce
    response = await handler(request)
    response.headers.setdefault('Content-Security-Policy', _POLICY.format(nonce=nonce))
    response.headers.setdefault('X-Content-Type-Options', 'nosniff')
    response.headers.setdefault('Referrer-Policy', 'no-referrer')
    return response


def nonce_of(request: web.Request) -> str:
    """The request's per-response nonce (for template contexts)."""
    value: Any = request.get(NONCE_KEY, '')
    return str(value)

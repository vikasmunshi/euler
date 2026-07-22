#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Cache-Control middleware: what a browser may reuse, and for how long (shared).

Every app-tier response says what it is worth keeping, because a response that
says *nothing* is the dangerous one: with no ``Cache-Control`` a browser is free
to apply **heuristic freshness** — reuse a response for a fraction of its age
since ``Last-Modified`` — so a file last touched months ago can be served from
cache for days without ever asking. That is the "why do I have to hard-refresh?"
bug, and it is invisible: it only bites the users who happened to have the old
copy (docs/web-server-guide.md § Caching).

Two classes, split on what the response *is*:

**Dynamic — ``no-store``.** Everything the app renders: pages, htmx fragments,
JSON. It is per-user, authenticated, and changes the moment its underlying file
does; there is no version of it worth keeping. ``no-store`` also keeps it out of
disk caches on shared machines, which is the right default for content behind a
login.

**Files — ``no-cache``.** A :class:`aiohttp.web.FileResponse`: bytes on disk,
identical for every user, and already carrying ``ETag``/``Last-Modified``.
``no-cache`` is not "do not cache" — it is "keep it, but revalidate before every
use", so an unchanged file costs one conditional request answered by a 304 while
a changed one is picked up immediately. Caddy applies the same rule to the
``/assets`` and ``/vendor`` trees it serves at the edge (scripts/setup/frontend.sh),
so a file behaves the same whichever tier hands it over.

Deliberately absent: any positive ``max-age``. Nothing this app serves is
addressed by a versioned URL, so nothing may be reused without asking — see the
guide for what would have to change first.
"""
from __future__ import annotations

__all__ = ['cache_middleware', 'NO_STORE', 'REVALIDATE', 'directive_for']

from typing import Awaitable, Callable

from aiohttp import web

#: Dynamic responses: never stored, always re-requested.
NO_STORE: str = 'no-store'
#: File responses: storable, but revalidated before every reuse (ETag → 304).
REVALIDATE: str = 'no-cache'

_Handler = Callable[[web.Request], Awaitable[web.StreamResponse]]


def directive_for(response: web.StreamResponse) -> str:
    """The ``Cache-Control`` value for *response* — by what it is, not what it says.

    A ``FileResponse`` is the only class with bytes on disk and validators to match;
    everything else (rendered HTML, htmx fragments, JSON) is dynamic.
    """
    return REVALIDATE if isinstance(response, web.FileResponse) else NO_STORE


def _stamp(response: web.StreamResponse) -> None:
    """Stamp the directive, unless the response has already gone out.

    ``setdefault``: a handler that has thought about its own caching keeps its say.
    A prepared response (a websocket, a stream mid-flight) has its headers on the
    wire already — mutating them there would be a silent no-op at best.
    """
    if response.prepared:
        return
    response.headers.setdefault('Cache-Control', directive_for(response))


@web.middleware
async def cache_middleware(request: web.Request, handler: _Handler) -> web.StreamResponse:
    """Stamp ``Cache-Control`` on every response — error responses included.

    A raised :class:`~aiohttp.web.HTTPException` *is* the response (a 404 page, a
    redirect to /login), and an unstamped one is heuristically cacheable like any
    other: a browser that cached "404" for a problem you have since written would
    keep serving it.
    """
    try:
        response = await handler(request)
    except web.HTTPException as exc:
        _stamp(exc)
        raise
    _stamp(response)
    return response

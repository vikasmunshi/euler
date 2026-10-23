#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Cache-Control middleware: what a browser may reuse, and for how long (shared).

Every app-tier response says what it is worth keeping, because a response that
says *nothing* is the dangerous one: with no `Cache-Control` a browser is free
to apply **heuristic freshness** — reuse a response for a fraction of its age
since `Last-Modified` — so a file last touched months ago can be served from
cache for days without ever asking. That is the "why do I have to hard-refresh?"
bug, and it is invisible: it only bites the users who happened to have the old
copy (docs/web-server-guide.md § Caching).

Two classes, split on what the response *is*:

**Dynamic — `no-store`.** Everything the app renders: pages, htmx fragments,
JSON. It is per-user, authenticated, and changes the moment its underlying file
does; there is no version of it worth keeping. `no-store` also keeps it out of
disk caches on shared machines, which is the right default for content behind a
login.

**Files — `no-cache`.** A :class:`aiohttp.web.FileResponse`: bytes on disk,
identical for every user, and already carrying `ETag`/`Last-Modified`.
`no-cache` is not "do not cache" — it is "keep it, but revalidate before every
use", so an unchanged file costs one conditional request answered by a 304 while
a changed one is picked up immediately. Caddy applies the same rule to a bare
`/assets` or `/vendor` path it serves at the edge (scripts/setup/frontend.sh),
so a file behaves the same whichever tier hands it over.

No positive `max-age` here: nothing this app serves is addressed by a versioned
URL. The edge's static trees are — the templates name each file by a hash of its
bytes (:mod:`euler_site.assets`) — and the edge alone marks those `immutable`.

**The public site's pages are the exception** (:func:`revalidated_middleware`). Signed out,
a page is the same for everyone and changes only when a deploy replaces the content package
and the code, so it can carry an `ETag` built from a fingerprint of that build: `public,
no-cache`, revalidated on every use like a file, and a matching `If-None-Match` is answered
with a 304 before anything is rendered.
"""
from __future__ import annotations

__all__ = ['cache_middleware', 'NO_STORE', 'PUBLIC_REVALIDATE', 'REVALIDATE', 'build_fingerprint', 'directive_for',
           'revalidated_middleware']

import hashlib
from pathlib import Path
from typing import Awaitable, Callable

from aiohttp import web
from aiohttp.typedefs import Middleware

from euler_site.csp import NONCE_KEY

#: Dynamic responses: never stored, always re-requested.
NO_STORE: str = 'no-store'
#: File responses: storable, but revalidated before every reuse (ETag → 304).
REVALIDATE: str = 'no-cache'
#: The public site's pages: the same for everyone, so a shared cache may keep them too —
#: still revalidated before every reuse.
PUBLIC_REVALIDATE: str = 'public, no-cache'
#: The request headers a public page's body depends on: htmx's fragment-or-page switch, and
#: the file route's view-or-embed switch. Without `Vary` a browser could reuse a fragment for
#: a full navigation of the same URL.
_VARY_ON: tuple[str, ...] = ('HX-Request', 'Sec-Fetch-Dest')

_Handler = Callable[[web.Request], Awaitable[web.StreamResponse]]


def directive_for(response: web.StreamResponse) -> str:
    """The `Cache-Control` value for *response* — by what it is, not what it says.

    A `FileResponse` is the only class with bytes on disk and validators to match;
    everything else (rendered HTML, htmx fragments, JSON) is dynamic.
    """
    return REVALIDATE if isinstance(response, web.FileResponse) else NO_STORE


def _stamp(response: web.StreamResponse) -> None:
    """Stamp the directive, unless the response has already gone out.

    `setdefault`: a handler that has thought about its own caching keeps its say.
    A prepared response (a websocket, a stream mid-flight) has its headers on the
    wire already — mutating them there would be a silent no-op at best.
    """
    if response.prepared:
        return
    response.headers.setdefault('Cache-Control', directive_for(response))


@web.middleware
async def cache_middleware(request: web.Request, handler: _Handler) -> web.StreamResponse:
    """Stamp `Cache-Control` on every response — error responses included.

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


def build_fingerprint(*roots: Path) -> str:
    """A digest of every file under *roots* — path, size and modification time.

    Computed once when the app starts. A deploy reinstalls the package and the content, so
    the fingerprint changes with every deploy and with nothing else.
    """
    digest = hashlib.sha256()
    for root in roots:
        for path in sorted(p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts):
            stat = path.stat()
            digest.update(f'{path.relative_to(root).as_posix()}\0{stat.st_size}\0{stat.st_mtime_ns}\n'.encode())
    return digest.hexdigest()


def revalidated_middleware(fingerprint: str) -> Middleware:
    """Validators for the public site's pages: an `ETag` per build and request variant.

    The tag is the build *fingerprint* plus everything the body depends on — the path and
    query and the :data:`_VARY_ON` headers — so it is known before the handler runs, and a
    matching `If-None-Match` is a 304 that renders nothing. Only successful GET/HEAD pages
    are tagged: a file keeps its own validators, and an error stays `no-store`.

    A page whose body carries its response's CSP nonce is left untagged: a 304 brings a
    fresh nonce in its header, and the stored body would no longer match it. No template
    uses the nonce today; this keeps one that starts to from breaking silently.
    """

    @web.middleware
    async def _middleware(request: web.Request, handler: _Handler) -> web.StreamResponse:
        if request.method not in ('GET', 'HEAD'):
            return await handler(request)
        variant = '\0'.join([fingerprint, request.path_qs, *(request.headers.get(h, '') for h in _VARY_ON)])
        etag = f'"{hashlib.sha256(variant.encode()).hexdigest()[:32]}"'
        headers = {'ETag': etag, 'Cache-Control': PUBLIC_REVALIDATE, 'Vary': ', '.join(_VARY_ON)}
        if etag in (tag.strip() for tag in request.headers.get('If-None-Match', '').split(',')):
            return web.Response(status=304, headers=headers)
        response = await handler(request)
        if response.status != 200 or isinstance(response, web.FileResponse) or response.prepared:
            return response
        body = response.body if isinstance(response, web.Response) else None
        nonce = request.get(NONCE_KEY, '')
        if not isinstance(body, bytes) or (nonce and nonce.encode() in body):
            return response
        response.headers.update(headers)
        return response

    return _middleware

#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Where a sign-in or a sign-out returns to: the page the reader was on.

Signing in and out are full-page trips through the auth service; without this, both land on
`/` and the reader loses their place. The page they were on travels as `next` — the login
link's `?next=`, the logout form's field, Caddy's redirect of an expired session — and comes
back through :func:`return_path`.

A `next` is attacker-controlled (anyone can send a link to `/login?next=…`), so it is an
**allowlist**, not a sanitiser: a path on this site, under one of the content routes the left
pane shows, or `/`. Anything else — another host (`//evil.example`, `/\\evil.example`, which
browsers treat as one), a scheme, an auth page, the terminal or an API route — returns `/`.
"""
from __future__ import annotations

__all__ = ['return_path']

from urllib.parse import urlsplit, urlunsplit

#: The left pane's routes, readable signed in or out (the public site serves them too).
_CONTENT: tuple[str, ...] = ('/solutions', '/docs', '/topics', '/about', '/shell')
#: Routes only a session can see: a fine place to return to after signing in, and not after
#: signing out (the page would only bounce to the login).
_SIGNED_IN: tuple[str, ...] = ('/account',)
#: Longer than any real page path; a `next` beyond it is not one.
_MAX: int = 512


def _under(path: str, prefixes: tuple[str, ...]) -> bool:
    return any(path == p or path.startswith(f'{p}/') for p in prefixes)


def return_path(raw: str | None, *, signed_in: bool) -> str:
    """*raw* if it names a page to return to — signed in, or (*signed_in* False) signed out —
    else `/`."""
    if not raw or len(raw) > _MAX or not raw.startswith('/') or raw[1:2] in ('/', '\\') \
            or any(ord(ch) < 0x20 or ch == '\\' for ch in raw):
        return '/'
    parts = urlsplit(raw)
    if parts.scheme or parts.netloc:
        return '/'
    allowed = parts.path == '/' or _under(parts.path, _CONTENT) or (signed_in and _under(parts.path, _SIGNED_IN))
    return urlunsplit(('', '', parts.path, parts.query, '')) if allowed else '/'

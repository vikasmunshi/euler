#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""HTTP layer for web authentication: SRP login endpoints + the gating middleware.

Login is browser-side SRP-6a — the password never reaches the server:

    POST /auth/challenge  {email}          -> {salt, B}
    POST /auth/verify     {email, A, M1}   -> {M2}  (+ sets the session cookie)
    GET  /logout                            -> clears the session

:func:`auth_middleware` requires a live session for every route except the login
page, its static assets, the two auth endpoints, and the favicon; a signed-out
browser navigation is redirected to ``/login?next=…`` while a programmatic fetch
gets 401. Unknown emails are answered with a stable decoy salt/B so the endpoints
do not reveal which accounts exist.
"""
from __future__ import annotations

__all__ = ['auth_middleware', 'setup_auth', 'is_authenticated']

import secrets
import time
from typing import Any
from urllib.parse import quote

from aiohttp import web
from aiohttp.typedefs import Handler

from solver.config import config
from solver.web.auth import policy
from solver.web.auth.sessions import SessionStore
from solver.web.auth.srp import SrpServer, decoy_token
from solver.web.auth.users import UserStore, normalize_email

#: Per-server auth state, stashed on the Application.
SESSIONS: web.AppKey[SessionStore] = web.AppKey('auth_sessions', SessionStore)
USERS: web.AppKey[UserStore] = web.AppKey('auth_users', UserStore)
# email -> (server, is_active, expiry): the outstanding SRP challenge per email.
PENDING: web.AppKey[dict[str, tuple[SrpServer, bool, float]]] = web.AppKey('auth_pending', dict)
# per-process secret backing the anti-enumeration decoy tokens.
DECOY_SECRET: web.AppKey[bytes] = web.AppKey('auth_decoy_secret', bytes)

#: Routes reachable without a session (so a signed-out browser can log in).
PUBLIC_PATHS: frozenset[str] = frozenset({
    '/login', '/logout', '/auth/challenge', '/auth/verify',
    '/favicon.ico', '/favicon.svg', '/login.css', '/login.js', '/srp-client.js',
})


def _wants_html(request: web.Request) -> bool:
    """True for a browser navigation (Accept lists text/html and not application/json)."""
    accept = request.headers.get('Accept', '')
    return 'text/html' in accept and 'application/json' not in accept


def _safe_next(raw: str | None) -> str:
    """Sanitise a post-login redirect target to a same-site absolute path."""
    if not raw or not raw.startswith('/') or raw.startswith('//'):
        return '/'
    return raw


def is_authenticated(request: web.Request) -> bool:
    """True if the request carries a live session cookie."""
    token = request.cookies.get(policy.SESSION_COOKIE)
    return request.app[SESSIONS].email_for(token) is not None


async def _serve_login(request: web.Request) -> web.StreamResponse:
    """Serve the login page, or bounce an already-authenticated visitor onward."""
    if is_authenticated(request):
        raise web.HTTPFound(_safe_next(request.query.get('next')))
    return web.FileResponse(config.static_file_dir / 'login' / 'login.html')


async def _read_json(request: web.Request) -> dict[str, Any]:
    """Parse a JSON object body, raising 400 for anything malformed."""
    try:
        data: Any = await request.json()
    except (ValueError, UnicodeDecodeError):
        raise web.HTTPBadRequest()
    if not isinstance(data, dict):
        raise web.HTTPBadRequest()
    return data


def _prune_pending(pending: dict[str, tuple[SrpServer, bool, float]]) -> None:
    """Drop expired outstanding challenges (bounds the map for unknown-email spam)."""
    now = time.time()
    for email in [e for e, (_s, _a, exp) in pending.items() if now >= exp]:
        pending.pop(email, None)


async def _auth_challenge(request: web.Request) -> web.StreamResponse:
    """`POST /auth/challenge {email}` → `{salt, B}` (decoy for unknown emails)."""
    data = await _read_json(request)
    email = normalize_email(str(data.get('email', '')))
    pending = request.app[PENDING]
    _prune_pending(pending)

    record = request.app[USERS].get(email)
    active = record is not None and not record.disabled
    token = record.token if record is not None else decoy_token(email, request.app[DECOY_SECRET])
    server = SrpServer(email, token)
    pending[email] = (server, active, time.time() + policy.CHALLENGE_TTL_SECONDS)
    return web.json_response({'salt': server.salt.hex(), 'B': format(server.public, 'x')})


async def _auth_verify(request: web.Request) -> web.StreamResponse:
    """`POST /auth/verify {email, A, M1}` → `{M2}` and open a session on success."""
    data = await _read_json(request)
    email = normalize_email(str(data.get('email', '')))
    entry = request.app[PENDING].pop(email, None)
    try:
        client_public = int(str(data['A']), 16)
        client_proof = bytes.fromhex(str(data['M1']))
    except (KeyError, ValueError):
        raise web.HTTPBadRequest()

    if entry is None or time.time() >= entry[2]:
        return _auth_failed()
    server, active, _expiry = entry
    try:
        server_proof = server.verify(client_public, client_proof)
    except ValueError:
        return _auth_failed()
    if not active:  # disabled account or a decoy for a nonexistent user
        return _auth_failed()

    sessions = request.app[SESSIONS]
    token = sessions.create(email)
    response = web.json_response({'M2': server_proof.hex()})
    response.set_cookie(policy.SESSION_COOKIE, token, max_age=sessions.ttl_seconds,
                        httponly=True, secure=True, samesite='Strict', path='/')
    return response


def _auth_failed() -> web.Response:
    """A uniform, non-revealing authentication-failure response."""
    return web.json_response({'error': 'authentication failed'}, status=401)


async def _logout(request: web.Request) -> web.StreamResponse:
    """Drop the current session and clear its cookie, then redirect to the login page."""
    request.app[SESSIONS].destroy(request.cookies.get(policy.SESSION_COOKIE))
    response = web.HTTPFound('/login')
    response.del_cookie(policy.SESSION_COOKIE, path='/')
    return response


@web.middleware
async def auth_middleware(request: web.Request, handler: Handler) -> web.StreamResponse:
    """Require a live session for every route except the public login surface."""
    if request.path in PUBLIC_PATHS or is_authenticated(request):
        return await handler(request)
    if _wants_html(request):
        raise web.HTTPFound(f'/login?next={quote(request.path_qs, safe="/?=&")}')
    raise web.HTTPUnauthorized(text='authentication required')


def setup_auth(app: web.Application) -> None:
    """Initialise per-server auth state and register the auth routes."""
    app[SESSIONS] = SessionStore(policy.SESSION_TTL_SECONDS)
    app[USERS] = UserStore(config.users_file)
    app[PENDING] = {}
    app[DECOY_SECRET] = secrets.token_bytes(32)
    app.add_routes([
        web.get('/login', _serve_login),
        web.post('/auth/challenge', _auth_challenge),
        web.post('/auth/verify', _auth_verify),
        web.get('/logout', _logout),
    ])

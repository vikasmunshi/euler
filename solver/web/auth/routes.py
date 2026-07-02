#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""HTTP layer for web authentication: SRP login endpoints + the gating middleware.

Login is browser-side SRP-6a — the password never reaches the server:

    POST /auth/challenge  {email}                    -> {salt, B}
    POST /auth/verify     {email, A, M1, remember?}  -> {M2}  (+ session cookie,
                                                              + remember cookie if asked)
    GET  /logout                                     -> clears the session + remember token

:func:`auth_middleware` requires a live session for every route except the login
page, its static assets, the auth/register endpoints, and the favicon; a signed-out
browser navigation is redirected to ``/login?next=…`` while a programmatic fetch
gets 401. A request with no session but a valid remember-me cookie is transparently
promoted to a fresh session (the remember token is rotated). Unknown emails are
answered with a stable decoy salt/B so the endpoints do not reveal which accounts exist.
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
from solver.web.auth.otp import PendingStore
from solver.web.auth.ratelimit import RateLimiter
from solver.web.auth.remember import RememberStore, load_or_create_secret
from solver.web.auth.sessions import SessionStore
from solver.web.auth.srp import SrpServer, SrpToken, decoy_token
from solver.web.auth.users import UserStore, normalize_email

#: Per-server auth state, stashed on the Application.
SESSIONS: web.AppKey[SessionStore] = web.AppKey('auth_sessions', SessionStore)
USERS: web.AppKey[UserStore] = web.AppKey('auth_users', UserStore)
PENDING_REG: web.AppKey[PendingStore] = web.AppKey('auth_pending_reg', PendingStore)
# email -> (server, is_active, expiry): the outstanding SRP challenge per email.
PENDING: web.AppKey[dict[str, tuple[SrpServer, bool, float]]] = web.AppKey('auth_pending', dict)
# per-process secret backing the anti-enumeration decoy tokens.
DECOY_SECRET: web.AppKey[bytes] = web.AppKey('auth_decoy_secret', bytes)
REMEMBER: web.AppKey[RememberStore] = web.AppKey('auth_remember', RememberStore)
LIMITER: web.AppKey[RateLimiter] = web.AppKey('auth_limiter', RateLimiter)

#: Routes reachable without a session (so a signed-out browser can log in).
PUBLIC_PATHS: frozenset[str] = frozenset({
    '/login', '/logout', '/auth/challenge', '/auth/verify',
    '/register', '/register/verify', '/register/complete',
    '/favicon.ico', '/favicon.svg', '/login.css', '/login.js', '/srp-client.js',
    '/register.css', '/register.js',
})

#: Unauthenticated endpoints rate-limited per client IP (brute-force surface).
RATE_LIMITED: frozenset[str] = frozenset({
    '/auth/challenge', '/auth/verify', '/register/verify', '/register/complete',
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


def _client_ip(request: web.Request) -> str:
    """Best-effort client IP: the first X-Forwarded-For hop (set by Caddy), else the peer."""
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.remote or 'unknown'


async def _add_security_headers(request: web.Request, response: web.StreamResponse) -> None:
    """Add conservative security headers to every response (on_response_prepare hook)."""
    response.headers.setdefault('X-Content-Type-Options', 'nosniff')
    response.headers.setdefault('X-Frame-Options', 'DENY')
    response.headers.setdefault('Referrer-Policy', 'no-referrer')


def is_authenticated(request: web.Request) -> bool:
    """True if the request carries a live session cookie (does not consider remember-me)."""
    token = request.cookies.get(policy.SESSION_COOKIE)
    return request.app[SESSIONS].email_for(token) is not None


def _set_auth_cookie(response: web.StreamResponse, name: str, value: str, max_age: int) -> None:
    """Set a hardened auth cookie (Secure, HttpOnly, SameSite=Strict, site-wide)."""
    response.set_cookie(name, value, max_age=max_age, httponly=True, secure=True,
                        samesite='Strict', path='/')


def current_email(request: web.Request) -> str:
    """The signed-in user's email (stashed by auth_middleware on every gated route)."""
    return str(request['user_email'])


def _resolve_auth(request: web.Request) -> tuple[str | None, list[tuple[str, str, int]]]:
    """Authenticate a request, promoting a remember-me cookie to a session if needed.

    Returns (email, cookies_to_set); email is None when unauthenticated. A live session
    needs no cookies; a successful remember-me promotion returns the fresh session +
    rotated remember cookies for the caller to apply to the response.
    """
    sessions = request.app[SESSIONS]
    email = sessions.email_for(request.cookies.get(policy.SESSION_COOKIE))
    if email is not None:
        return email, []
    rotated = request.app[REMEMBER].validate_and_rotate(request.cookies.get(policy.REMEMBER_COOKIE))
    if rotated is None:
        return None, []
    remember_email, new_remember = rotated
    return remember_email, [
        (policy.SESSION_COOKIE, sessions.create(remember_email), sessions.ttl_seconds),
        (policy.REMEMBER_COOKIE, new_remember, request.app[REMEMBER].ttl_seconds),
    ]


def _apply_cookies(response: web.StreamResponse, cookies: list[tuple[str, str, int]]) -> None:
    """Apply the (name, value, max_age) cookies from a remember-me promotion."""
    for name, value, max_age in cookies:
        _set_auth_cookie(response, name, value, max_age)


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
    if record is not None and record.registered:
        token = record.token
        active = not record.disabled
    else:  # unknown, or invited-but-not-registered → indistinguishable decoy
        token = decoy_token(email, request.app[DECOY_SECRET])
        active = False
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
    response = web.json_response({'M2': server_proof.hex()})
    _set_auth_cookie(response, policy.SESSION_COOKIE, sessions.create(email), sessions.ttl_seconds)
    if bool(data.get('remember')):
        remember = request.app[REMEMBER]
        _set_auth_cookie(response, policy.REMEMBER_COOKIE, remember.issue(email), remember.ttl_seconds)
    return response


def _auth_failed() -> web.Response:
    """A uniform, non-revealing authentication-failure response."""
    return web.json_response({'error': 'authentication failed'}, status=401)


async def _serve_register(request: web.Request) -> web.StreamResponse:
    """Serve the registration page (public; invited users complete signup here)."""
    return web.FileResponse(config.static_file_dir / 'register' / 'register.html')


async def _register_verify(request: web.Request) -> web.StreamResponse:
    """`POST /register/verify {email, otp}` → 200 if the OTP is currently valid (a UX pre-check).

    Does not consume the OTP; the authoritative check happens in `/register/complete`.
    """
    data = await _read_json(request)
    email = normalize_email(str(data.get('email', '')))
    otp = str(data.get('otp', ''))
    if request.app[PENDING_REG].check(email, otp, consume=False):
        return web.json_response({'ok': True})
    return _auth_failed()


async def _register_complete(request: web.Request) -> web.StreamResponse:
    """`POST /register/complete {email, otp, salt, verifier}` → store the verifier + enable.

    The browser has verified the OTP, taken the chosen password (checked against the
    complexity policy client-side), and computed the SRP salt/verifier. A valid OTP is
    the authorisation to set them; the OTP is consumed on success.
    """
    data = await _read_json(request)
    email = normalize_email(str(data.get('email', '')))
    otp = str(data.get('otp', ''))
    try:
        token = SrpToken(salt=bytes.fromhex(str(data['salt'])), verifier=int(str(data['verifier']), 16))
    except (KeyError, ValueError):
        raise web.HTTPBadRequest()
    if not request.app[PENDING_REG].check(email, otp, consume=True):
        return _auth_failed()
    request.app[USERS].register(email, token)
    return web.json_response({'ok': True})


async def _logout(request: web.Request) -> web.StreamResponse:
    """Drop the session and remember token, clear both cookies, redirect to the login page."""
    request.app[SESSIONS].destroy(request.cookies.get(policy.SESSION_COOKIE))
    request.app[REMEMBER].revoke(request.cookies.get(policy.REMEMBER_COOKIE))
    response = web.HTTPFound('/login')
    response.del_cookie(policy.SESSION_COOKIE, path='/')
    response.del_cookie(policy.REMEMBER_COOKIE, path='/')
    return response


async def _whoami(request: web.Request) -> web.StreamResponse:
    """`GET /whoami` → `{email}` for the signed-in user (the password page needs it for SRP)."""
    return web.json_response({'email': current_email(request)})


async def _serve_password(request: web.Request) -> web.StreamResponse:
    """Serve the self-service change-password page (authenticated)."""
    return web.FileResponse(config.static_file_dir / 'password' / 'password.html')


async def _password_change(request: web.Request) -> web.StreamResponse:
    """`POST /password/change {salt, verifier}` → set a new SRP verifier for the signed-in user.

    Authorised by the session (already logged in); the email comes from the session, not
    the body. Revokes remember-me tokens so other devices must re-authenticate.
    """
    data = await _read_json(request)
    try:
        token = SrpToken(salt=bytes.fromhex(str(data['salt'])), verifier=int(str(data['verifier']), 16))
    except (KeyError, ValueError):
        raise web.HTTPBadRequest()
    email = current_email(request)
    request.app[USERS].register(email, token)
    request.app[REMEMBER].revoke_all(email)
    return web.json_response({'ok': True})


@web.middleware
async def auth_middleware(request: web.Request, handler: Handler) -> web.StreamResponse:
    """Gate every route but the public login surface; promote remember-me to a session."""
    if request.path in RATE_LIMITED and not request.app[LIMITER].allow(_client_ip(request)):
        raise web.HTTPTooManyRequests(text='too many requests')
    if request.path in PUBLIC_PATHS:
        return await handler(request)
    email, cookies = _resolve_auth(request)
    if email is None:
        if _wants_html(request):
            raise web.HTTPFound(f'/login?next={quote(request.path_qs, safe="/?=&")}')
        raise web.HTTPUnauthorized(text='authentication required')
    request['user_email'] = email
    try:
        response = await handler(request)
    except web.HTTPException as exc:
        _apply_cookies(exc, cookies)   # a promoted request that redirects still gets its cookies
        raise
    _apply_cookies(response, cookies)
    if _wants_html(request):
        # Never cache a gated page document, or the browser would serve it after logout
        # (and via the back button) without re-hitting the now-redirecting server.
        response.headers['Cache-Control'] = 'no-store'
    return response


def setup_auth(app: web.Application) -> None:
    """Initialise per-server auth state and register the auth routes."""
    app[SESSIONS] = SessionStore(policy.SESSION_TTL_SECONDS)
    app[USERS] = UserStore(config.users_file)
    app[PENDING_REG] = PendingStore(config.pending_file)
    app[REMEMBER] = RememberStore(config.remember_file,
                                  load_or_create_secret(config.session_secret_file),
                                  policy.REMEMBER_TTL_SECONDS)
    app[PENDING] = {}
    app[DECOY_SECRET] = secrets.token_bytes(32)
    app[LIMITER] = RateLimiter(policy.AUTH_RATE_MAX, policy.AUTH_RATE_WINDOW_SECONDS)
    app.on_response_prepare.append(_add_security_headers)
    app.add_routes([
        web.get('/login', _serve_login),
        web.post('/auth/challenge', _auth_challenge),
        web.post('/auth/verify', _auth_verify),
        web.get('/register', _serve_register),
        web.post('/register/verify', _register_verify),
        web.post('/register/complete', _register_complete),
        web.get('/whoami', _whoami),
        web.get('/password', _serve_password),
        web.post('/password/change', _password_change),
        web.get('/logout', _logout),
    ])

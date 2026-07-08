#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The auth service: public + admin aiohttp apps over unix sockets (DD-6/DD-9).

Two listeners, one process, one owner of all auth state:

- **Public** (``/run/euler/auth.sock``, group ``euler-web``) — reached through
  Caddy: SRP login (challenge/verify), session resume/logout, and the
  ``forward_auth`` endpoint (``200 + X-User + X-Profile`` or ``401``). The
  shell-ticket endpoints (DD-9) also live here but are **not routed by Caddy**
  — only socket peers (the ws service, the PTY shells) can reach them.
- **Admin** (``/run/euler-adm/auth-admin.sock``, ``0600`` euler-auth-private)
  — the local admin plane (DD-6), never routed through Caddy and **wheel-gated**:
  only root (the operator, via sudo) can connect, and ``X-Admin-Token`` (kept
  solely in root-readable ``/etc/euler/auth.env``) is a second check. ``users``
  add / list / enable / disable / remove.

Access logging is disabled on both listeners: registration/reset URLs carry
link tokens in the query string and must never reach the journal. App-level
events are logged without secrets instead.
"""
from __future__ import annotations

__all__ = ['AuthService', 'build_public_app', 'build_admin_app']

import asyncio
import hmac
import logging
import secrets
import time
from datetime import datetime, timezone
from typing import Any

from aiohttp import web

from solver.web.auth import policy
from solver.web.auth.config import AuthConfig
from solver.web.auth.mail import Mailer
from solver.web.auth.pending import PendingStore
from solver.web.auth.ratelimit import RateLimiter
from solver.web.auth.remember import RememberStore, load_or_create_secret
from solver.web.auth.sessions import SessionStore
from solver.web.auth.srp import SrpServer, decoy_token
from solver.web.auth.tickets import TicketStore
from solver.web.auth.users import UserStore, normalize_email

log = logging.getLogger('euler-auth')

_GENERIC_401 = 'authentication failed'


def _client_key(request: web.Request) -> str:
    """The rate-limit key: the first X-Forwarded-For hop (Caddy sets it), else 'local'."""
    forwarded = request.headers.get('X-Forwarded-For', '')
    return forwarded.split(',')[0].strip() or 'local'


async def _json_body(request: web.Request) -> dict[str, Any]:
    """The request's JSON object body; an empty dict for anything malformed."""
    try:
        data = await request.json()
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


class AuthService:
    """All auth state and behaviour; the route handlers are thin wrappers over this."""

    def __init__(self, config: AuthConfig) -> None:
        self.config = config
        state = config.state_dir
        self.users = UserStore(state / 'users.json')
        self.pending = PendingStore(state / 'pending.json')
        self.remember = RememberStore(state / 'remember.json',
                                      load_or_create_secret(state / 'session-secret'))
        self.sessions = SessionStore(policy.SESSION_TTL_SECONDS)
        self.tickets = TicketStore()
        self.mailer = Mailer(config.smtp_relay, config.base_url)
        self.rate = RateLimiter(policy.AUTH_RATE_MAX, policy.AUTH_RATE_WINDOW_SECONDS)
        #: In-flight SRP handshakes: email → (server, expiry). One per email at a time.
        self._challenges: dict[str, tuple[SrpServer, float]] = {}
        #: Per-process secret for stable decoy salts (unknown-email challenges).
        self._decoy_secret = secrets.token_bytes(32)

    # ── sessions & cookies ────────────────────────────────────────────────────────

    def session_identity(self, request: web.Request) -> tuple[str, str] | None:
        """``(email, profile)`` for the request's session cookie, or None."""
        return self.sessions.get(request.cookies.get(policy.SESSION_COOKIE))

    @staticmethod
    def _set_cookie(response: web.Response, name: str, value: str, max_age: int) -> None:
        response.set_cookie(name, value, max_age=max_age, path='/',
                            secure=True, httponly=True, samesite='Lax')

    def open_session(self, response: web.Response, email: str, profile: str,
                     *, remember: bool) -> None:
        """Create the session (and optionally a remember-me token) as cookies on *response*."""
        token = self.sessions.create(email, profile)
        self._set_cookie(response, policy.SESSION_COOKIE, token, policy.SESSION_TTL_SECONDS)
        if remember:
            cookie = self.remember.issue(email)
            self._set_cookie(response, policy.REMEMBER_COOKIE, cookie, policy.REMEMBER_TTL_SECONDS)

    # ── SRP handshake ─────────────────────────────────────────────────────────────

    def start_challenge(self, email: str) -> tuple[str, str]:
        """Begin a handshake for *email*; return ``(salt_hex, B_hex)``.

        Unknown or disabled accounts get a stable **decoy** challenge (same shape,
        never stored), so the response does not reveal whether the account exists.
        """
        key = normalize_email(email)
        now = time.time()
        self._challenges = {k: v for k, v in self._challenges.items() if v[1] > now}
        user = self.users.get(key)
        if user is None or user.disabled or not user.verifier:
            server = SrpServer(key, decoy_token(key, self._decoy_secret))
            return server.salt.hex(), f'{server.public:x}'
        server = SrpServer(key, user.srp_token)
        self._challenges[key] = (server, now + policy.CHALLENGE_TTL_SECONDS)
        return server.salt.hex(), f'{server.public:x}'

    def finish_challenge(self, email: str, client_public_hex: str,
                         client_proof_hex: str) -> tuple[str, str] | None:
        """Verify the client proof; return ``(M2_hex, profile)`` or None (generic failure)."""
        key = normalize_email(email)
        entry = self._challenges.pop(key, None)
        if entry is None or entry[1] <= time.time():
            return None
        server = entry[0]
        try:
            proof = server.verify(int(client_public_hex, 16), bytes.fromhex(client_proof_hex))
        except ValueError:
            return None
        user = self.users.get(key)
        if user is None or user.disabled:      # re-check: state may have moved under us
            return None
        return proof.hex(), user.profile

    # ── account lifecycle (admin plane) ───────────────────────────────────────────

    def invite(self, email: str, profile: str) -> str:
        """Mint a registration invite and email the link; return the invite URL (DD-7)."""
        token = self.pending.mint(email, profile, 'register')
        url = f'{self.config.base_url}/register?token={token}'
        self.mailer.send_invite(email, token, 'register')
        return url

    def revoke_access(self, email: str) -> None:
        """Kill live access for *email* everywhere (disable/remove)."""
        self.sessions.revoke_email(email)
        self.remember.revoke_email(email)
        self.pending.revoke_email(email)


# ── public app (auth.sock — via Caddy, plus the socket-peer ticket endpoints) ──────

def build_public_app(service: AuthService) -> web.Application:
    """The public listener: login, forward_auth, session, and shell tickets."""

    async def healthz(_request: web.Request) -> web.Response:
        return web.Response(text='ok')

    async def check(request: web.Request) -> web.Response:
        """The Caddy ``forward_auth`` endpoint: 200 + identity headers, or 401."""
        identity = service.session_identity(request)
        if identity is None:
            return web.Response(status=401, text=_GENERIC_401)
        email, profile = identity
        return web.Response(status=200, headers={'X-User': email, 'X-Profile': profile})

    async def challenge(request: web.Request) -> web.Response:
        if not service.rate.allow(_client_key(request)):
            return web.Response(status=429, text='rate limited')
        body = await _json_body(request)
        email = str(body.get('email', ''))
        if '@' not in email:
            return web.Response(status=400, text='email required')
        salt_hex, public_hex = service.start_challenge(email)
        return web.json_response({'salt': salt_hex, 'B': public_hex})

    async def verify(request: web.Request) -> web.Response:
        if not service.rate.allow(_client_key(request)):
            return web.Response(status=429, text='rate limited')
        body = await _json_body(request)
        try:
            result = service.finish_challenge(str(body.get('email', '')),
                                              str(body.get('A', '')), str(body.get('M1', '')))
        except ValueError:
            result = None
        if result is None:
            log.info('login failed for %s', normalize_email(str(body.get('email', '?'))))
            return web.Response(status=401, text=_GENERIC_401)
        server_proof_hex, profile = result
        email = normalize_email(str(body.get('email', '')))
        response = web.json_response({'M2': server_proof_hex, 'email': email, 'profile': profile})
        service.open_session(response, email, profile, remember=bool(body.get('remember', False)))
        log.info('login ok for %s (%s)', email, profile)
        return response

    async def resume(request: web.Request) -> web.Response:
        """Redeem a remember-me cookie for a fresh session (rotating the token)."""
        if not service.rate.allow(_client_key(request)):
            return web.Response(status=429, text='rate limited')
        cookie = request.cookies.get(policy.REMEMBER_COOKIE, '')
        redeemed = service.remember.redeem(cookie) if cookie else None
        if redeemed is None:
            return web.Response(status=401, text=_GENERIC_401)
        email, new_cookie = redeemed
        user = service.users.get(email)
        if user is None or user.disabled:
            return web.Response(status=401, text=_GENERIC_401)
        response = web.json_response({'email': email, 'profile': user.profile})
        token = service.sessions.create(email, user.profile)
        service._set_cookie(response, policy.SESSION_COOKIE, token, policy.SESSION_TTL_SECONDS)
        service._set_cookie(response, policy.REMEMBER_COOKIE, new_cookie, policy.REMEMBER_TTL_SECONDS)
        log.info('session resumed for %s', email)
        return response

    async def logout(request: web.Request) -> web.Response:
        service.sessions.drop(request.cookies.get(policy.SESSION_COOKIE))
        remember_cookie = request.cookies.get(policy.REMEMBER_COOKIE)
        if remember_cookie:
            service.remember.revoke(remember_cookie)
        response = web.json_response({'ok': True})
        response.del_cookie(policy.SESSION_COOKIE, path='/')
        response.del_cookie(policy.REMEMBER_COOKIE, path='/')
        return response

    async def ticket_mint(request: web.Request) -> web.Response:
        """Mint a one-time shell ticket against the caller's live session (DD-9).

        Not routed by Caddy: only socket peers (the ws service, forwarding the
        user's cookie) reach this. A shell user cannot mint — no cookie.
        """
        identity = service.session_identity(request)
        if identity is None:
            return web.Response(status=401, text=_GENERIC_401)
        email, profile = identity
        ticket = service.tickets.mint(email, profile)
        log.info('shell ticket minted for %s', email)
        return web.json_response({'ticket': ticket})

    async def ticket_redeem(request: web.Request) -> web.Response:
        """Consume a shell ticket, returning the authoritative identity (DD-9)."""
        body = await _json_body(request)
        redeemed = service.tickets.redeem(str(body.get('ticket', '')))
        if redeemed is None:
            return web.Response(status=401, text='invalid ticket')
        email, profile = redeemed
        log.info('shell ticket redeemed for %s', email)
        return web.json_response({'email': email, 'profile': profile})

    app = web.Application()
    app.add_routes([
        web.get('/healthz', healthz),
        web.get('/auth/check', check),
        web.post('/auth/challenge', challenge),
        web.post('/auth/verify', verify),
        web.post('/auth/resume', resume),
        web.post('/auth/logout', logout),
        web.post('/shell-ticket', ticket_mint),
        web.post('/shell-ticket/redeem', ticket_redeem),
    ])
    return app


# ── admin app (auth-admin.sock — local only, never via Caddy) ──────────────────────

def build_admin_app(service: AuthService) -> web.Application:
    """The admin plane (DD-6): account lifecycle behind the euler-adm socket + token."""

    @web.middleware
    async def require_token(request: web.Request,
                            handler: Any) -> web.StreamResponse:
        if request.path != '/healthz':
            token = request.headers.get('X-Admin-Token', '')
            if not hmac.compare_digest(token, service.config.admin_token):
                return web.Response(status=401, text='bad admin token')
        return await handler(request)  # type: ignore[no-any-return]

    async def healthz(_request: web.Request) -> web.Response:
        return web.Response(text='ok')

    async def list_users(_request: web.Request) -> web.Response:
        return web.json_response({
            'users': [user.summary() for user in service.users.all()],
            'pending': [record.summary() for record in service.pending.all()],
        })

    async def add_user(request: web.Request) -> web.Response:
        """Mint + mail an invite (DD-7 step 1). No user record exists until completion."""
        body = await _json_body(request)
        email = normalize_email(str(body.get('email', '')))
        profile = str(body.get('profile', 'user'))
        if '@' not in email:
            return web.Response(status=400, text='valid email required')
        if profile not in policy.PROFILES:
            return web.Response(status=400, text=f'profile must be one of {policy.PROFILES}')
        if service.users.get(email) is not None:
            return web.Response(status=409, text='user already registered')
        try:
            # In a thread: the mail submission is blocking smtplib, and the
            # upstream (relay → Gmail) can take many seconds — the event loop
            # must keep serving forward_auth meanwhile.
            url = await asyncio.to_thread(service.invite, email, profile)
        except OSError as exc:
            log.warning('invite mail to %s failed: %s', email, exc)
            return web.Response(status=502, text=f'invite mail failed: {exc}')
        log.info('invited %s (%s)', email, profile)
        return web.json_response({'email': email, 'profile': profile, 'invite_url': url,
                                  'expires': f'{policy.INVITE_TTL_SECONDS // 86400}d'}, status=201)

    async def set_enabled(request: web.Request) -> web.Response:
        email = normalize_email(request.match_info['email'])
        enable = request.match_info['action'] == 'enable'
        if not service.users.set_enabled(email, enable):
            return web.Response(status=404, text='no such user')
        if not enable:
            service.revoke_access(email)
        log.info('%s %s', 'enabled' if enable else 'disabled', email)
        return web.json_response({'email': email, 'disabled': not enable})

    async def remove_user(request: web.Request) -> web.Response:
        email = normalize_email(request.match_info['email'])
        existed = service.users.remove(email)
        revoked = service.pending.revoke_email(email)
        service.revoke_access(email)
        if not existed and not revoked:
            return web.Response(status=404, text='no such user or invite')
        log.info('removed %s', email)
        return web.json_response({'email': email, 'removed': True})

    app = web.Application(middlewares=[require_token])
    app.add_routes([
        web.get('/healthz', healthz),
        web.get('/admin/users', list_users),
        web.post('/admin/users', add_user),
        web.post('/admin/users/{email}/{action:enable|disable}', set_enabled),
        web.delete('/admin/users/{email}', remove_user),
    ])
    return app


def utcnow_iso() -> str:
    """Current UTC time in ISO-8601 (shared by the DD-7 flow handlers, step 4)."""
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

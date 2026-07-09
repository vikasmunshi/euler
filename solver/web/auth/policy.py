#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Auth policy constants (lifetimes, cookie names, password and OTP rules).

Kept in one place so the server and (where relevant) the browser client agree.
Values implement the locked design decisions DD-6/DD-7/DD-9 in
docs/secure-web-server.md.
"""
from __future__ import annotations

__all__ = ['SESSION_COOKIE', 'SESSION_TTL_SECONDS', 'CHALLENGE_TTL_SECONDS', 'MIN_PASSWORD_LENGTH',
           'PASSWORD_REQUIRE_CLASSES', 'INVITE_TTL_SECONDS', 'LINK_TOKEN_BYTES',
           'OTP_DIGITS', 'OTP_TTL_SECONDS', 'OTP_MAX_ATTEMPTS', 'OTP_MAX_SENDS',
           'REMEMBER_COOKIE', 'REMEMBER_TTL_SECONDS', 'AUTH_RATE_MAX', 'AUTH_RATE_WINDOW_SECONDS',
           'TICKET_TTL_SECONDS', 'PROFILES']

#: A user's authorization profile, in descending order of privilege (drives
#: command/route authorization; see solver/commands.csv and docs/access-control.md).
PROFILES: tuple[str, ...] = ('admin', 'user', 'guest')

#: Name of the short-lived session cookie set on a successful SRP login.
SESSION_COOKIE: str = 'solver_session'
#: Session lifetime — 12 hours (in-memory; a service restart drops sessions, DD-6).
SESSION_TTL_SECONDS: int = 12 * 3600
#: How long a pending SRP challenge (server ephemeral B) is held between the
#: challenge and verify steps.
CHALLENGE_TTL_SECONDS: int = 120
#: Minimum password length. The user chooses their password in the browser during
#: registration, so the browser enforces this; the server never sees the password.
MIN_PASSWORD_LENGTH: int = 16
#: Character classes a password must draw from (all four): lower + upper + digit +
#: special. Enforced client-side (mirrored in the registration page) since the
#: server never sees the password; documented here as the single source of truth.
PASSWORD_REQUIRE_CLASSES: tuple[str, ...] = ('lower', 'upper', 'digit', 'special')

#: How long the emailed invite / reset link remains valid — 7 days (DD-7).
INVITE_TTL_SECONDS: int = 7 * 24 * 3600
#: Entropy (bytes) of the secure invite / reset link token.
LINK_TOKEN_BYTES: int = 32

#: The emailed one-time code proving live mailbox control at completion time (DD-7).
OTP_DIGITS: int = 6
#: OTP lifetime — 10 minutes.
OTP_TTL_SECONDS: int = 10 * 60
#: Failed tries before the OTP is invalidated (a fresh one must be requested).
OTP_MAX_ATTEMPTS: int = 5
#: OTP (re)sends per pending record before the invite itself must be re-minted.
OTP_MAX_SENDS: int = 5

#: Name of the persistent "remember me" cookie (a rotating selector:validator token).
REMEMBER_COOKIE: str = 'solver_remember'
#: Remember-me lifetime — 30 days (rotated on each use).
REMEMBER_TTL_SECONDS: int = 30 * 24 * 3600

#: Per-client rate limit on the unauthenticated auth/register endpoints.
AUTH_RATE_MAX: int = 30
AUTH_RATE_WINDOW_SECONDS: int = 60

#: One-time shell ticket lifetime (DD-9): minted against a live session at WS
#: attach, redeemed by the PTY child at startup — 60 seconds covers the fork.
TICKET_TTL_SECONDS: int = 60

#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Auth policy constants (lifetimes, cookie names, password rules).

Kept in one place so the server and (where relevant) the browser client agree.
Values match the design in docs/tls-and-auth.md.
"""
from __future__ import annotations

__all__ = ['SESSION_COOKIE', 'SESSION_TTL_SECONDS', 'CHALLENGE_TTL_SECONDS', 'MIN_PASSWORD_LENGTH',
           'PASSWORD_REQUIRE_CLASSES', 'REGISTRATION_TTL_SECONDS', 'REGISTRATION_TOKEN_BYTES',
           'REMEMBER_COOKIE', 'REMEMBER_TTL_SECONDS', 'AUTH_RATE_MAX', 'AUTH_RATE_WINDOW_SECONDS']

#: Name of the short-lived session cookie set on a successful SRP login.
SESSION_COOKIE: str = 'solver_session'
#: Session lifetime — 12 hours.
SESSION_TTL_SECONDS: int = 12 * 3600
#: How long a pending SRP challenge (server ephemeral B) is held between the
#: challenge and verify steps.
CHALLENGE_TTL_SECONDS: int = 120
#: Minimum password length. The user chooses their password in the browser during
#: registration, so the browser enforces this; the server never sees the password.
MIN_PASSWORD_LENGTH: int = 16
#: Character classes a password must draw from (all four): lower + upper + digit +
#: special. Enforced client-side (mirrored in srp-client.js) since the server never
#: sees the password; documented here as the single source of truth.
PASSWORD_REQUIRE_CLASSES: tuple[str, ...] = ('lower', 'upper', 'digit', 'special')

#: How long the emailed registration / reset link remains valid — 24 hours.
REGISTRATION_TTL_SECONDS: int = 24 * 3600
#: Entropy (bytes) of the secure registration / reset link token.
REGISTRATION_TOKEN_BYTES: int = 32

#: Name of the persistent "remember me" cookie (a rotating selector:validator token).
REMEMBER_COOKIE: str = 'solver_remember'
#: Remember-me lifetime — 30 days (refreshed on each use).
REMEMBER_TTL_SECONDS: int = 30 * 24 * 3600

#: Per-client-IP rate limit on the unauthenticated auth/register endpoints.
AUTH_RATE_MAX: int = 30
AUTH_RATE_WINDOW_SECONDS: int = 60

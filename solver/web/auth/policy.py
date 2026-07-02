#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Auth policy constants (lifetimes, cookie names, password rules).

Kept in one place so the server and (where relevant) the browser client agree.
Values match the confirmed decisions in docs/auth-plan.md.
"""
from __future__ import annotations

__all__ = ['SESSION_COOKIE', 'SESSION_TTL_SECONDS', 'CHALLENGE_TTL_SECONDS', 'MIN_PASSWORD_LENGTH',
           'OTP_LENGTH', 'OTP_TTL_SECONDS', 'OTP_MAX_ATTEMPTS', 'REMEMBER_COOKIE', 'REMEMBER_TTL_SECONDS',
           'AUTH_RATE_MAX', 'AUTH_RATE_WINDOW_SECONDS']

#: Name of the short-lived session cookie set on a successful SRP login.
SESSION_COOKIE: str = 'solver_session'
#: Session lifetime — 12 hours.
SESSION_TTL_SECONDS: int = 12 * 3600
#: How long a pending SRP challenge (server ephemeral B) is held between the
#: challenge and verify steps.
CHALLENGE_TTL_SECONDS: int = 120
#: Minimum password length. The user chooses their password in the browser during
#: registration, so the browser enforces this; the server never sees the password.
MIN_PASSWORD_LENGTH: int = 12

#: Registration one-time-password: number of decimal digits.
OTP_LENGTH: int = 6
#: How long an emailed OTP remains valid — 10 minutes.
OTP_TTL_SECONDS: int = 10 * 60
#: Wrong-OTP attempts allowed before a pending registration is locked out.
OTP_MAX_ATTEMPTS: int = 5

#: Name of the persistent "remember me" cookie (a rotating selector:validator token).
REMEMBER_COOKIE: str = 'solver_remember'
#: Remember-me lifetime — 30 days (refreshed on each use).
REMEMBER_TTL_SECONDS: int = 30 * 24 * 3600

#: Per-client-IP rate limit on the unauthenticated auth/register endpoints.
AUTH_RATE_MAX: int = 30
AUTH_RATE_WINDOW_SECONDS: int = 60

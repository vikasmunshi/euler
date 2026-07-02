#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Auth policy constants (lifetimes, cookie names, password rules).

Kept in one place so the server and (where relevant) the browser client agree.
Values match the confirmed decisions in docs/auth-plan.md.
"""
from __future__ import annotations

__all__ = ['SESSION_COOKIE', 'SESSION_TTL_SECONDS', 'CHALLENGE_TTL_SECONDS', 'MIN_PASSWORD_LENGTH',
           'OTP_LENGTH', 'OTP_TTL_SECONDS', 'OTP_MAX_ATTEMPTS']

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

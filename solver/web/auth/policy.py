#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Auth policy constants (lifetimes, cookie names, password rules).

Kept in one place so the server and (where relevant) the browser client agree.
Values match the confirmed decisions in docs/auth-plan.md.
"""
from __future__ import annotations

__all__ = ['SESSION_COOKIE', 'SESSION_TTL_SECONDS', 'CHALLENGE_TTL_SECONDS', 'MIN_PASSWORD_LENGTH']

#: Name of the short-lived session cookie set on a successful SRP login.
SESSION_COOKIE: str = 'solver_session'
#: Session lifetime — 12 hours.
SESSION_TTL_SECONDS: int = 12 * 3600
#: How long a pending SRP challenge (server ephemeral B) is held between the
#: challenge and verify steps.
CHALLENGE_TTL_SECONDS: int = 120
#: Minimum password length enforced where the server sees the password (the local
#: `users add` bootstrap). Browser-side registration mirrors this (milestone 3).
MIN_PASSWORD_LENGTH: int = 12

#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""In-memory web session table (DD-6).

A logged-in browser holds an opaque random token in a cookie; this maps that
token to ``(email, profile)`` and an expiry. State is per-process by design: a
service restart logs everyone out, and remember-me tokens
(:mod:`solver.web.auth.remember`) restore sessions across restarts.
"""
from __future__ import annotations

__all__ = ['SessionStore']

import secrets
import time

from solver.web.auth.users import normalize_email


class SessionStore:
    """Opaque-token → (email, profile, expiry) map with lazy expiry eviction."""

    def __init__(self, ttl_seconds: int) -> None:
        self._ttl = ttl_seconds
        self._sessions: dict[str, tuple[str, str, float]] = {}

    def create(self, email: str, profile: str) -> str:
        """Open a session; return the fresh opaque cookie token."""
        token = secrets.token_urlsafe(32)
        self._sessions[token] = (normalize_email(email), profile, time.time() + self._ttl)
        return token

    def get(self, token: str | None) -> tuple[str, str] | None:
        """Return ``(email, profile)`` for a live token, or None (evicting expired)."""
        if not token:
            return None
        entry = self._sessions.get(token)
        if entry is None:
            return None
        email, profile, expiry = entry
        if time.time() >= expiry:
            self._sessions.pop(token, None)
            return None
        return email, profile

    def drop(self, token: str | None) -> None:
        """Close the session for *token* (logout)."""
        if token:
            self._sessions.pop(token, None)

    def revoke_email(self, email: str) -> int:
        """Close every session for *email* (disable/remove); return how many."""
        key_email = normalize_email(email)
        doomed = [token for token, (owner, _, _) in self._sessions.items() if owner == key_email]
        for token in doomed:
            del self._sessions[token]
        return len(doomed)

#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""In-memory web session table.

A logged-in browser holds an opaque random token in a cookie; this maps that
token to the user's email and an expiry. State is per-process, so restarting the
server logs everyone out (remember-me tokens, milestone 4, restore sessions
across restarts). No session data is persisted here.
"""
from __future__ import annotations

__all__ = ['SessionStore']

import secrets
import time


class SessionStore:
    """Opaque-token → (email, expiry) map with lazy expiry eviction."""

    def __init__(self, ttl_seconds: int) -> None:
        self._ttl: int = ttl_seconds
        self._sessions: dict[str, tuple[str, float]] = {}

    def create(self, email: str) -> str:
        """Open a session for `email`; return the fresh opaque token."""
        token: str = secrets.token_urlsafe(32)
        self._sessions[token] = (email, time.time() + self._ttl)
        return token

    def email_for(self, token: str | None) -> str | None:
        """Return the email for a live token, or None if absent/expired (evicting it)."""
        if token is None:
            return None
        entry = self._sessions.get(token)
        if entry is None:
            return None
        email, expiry = entry
        if time.time() >= expiry:
            self._sessions.pop(token, None)
            return None
        return email

    def destroy(self, token: str | None) -> None:
        """Drop a session token if present (idempotent)."""
        if token is not None:
            self._sessions.pop(token, None)

    @property
    def ttl_seconds(self) -> int:
        """The configured session lifetime, for setting the cookie max-age."""
        return self._ttl

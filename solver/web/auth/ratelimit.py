#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""A small in-memory sliding-window rate limiter for the auth endpoints.

Slows brute force against the unauthenticated login/registration endpoints:
at most `max_requests` per `window_seconds` for a given key (the client IP). It
is per-process and best-effort — coarse defense-in-depth alongside the single-use
secure-link tokens and SRP itself, not a distributed quota.
"""
from __future__ import annotations

__all__ = ['RateLimiter']

import time

#: Above this many tracked keys, drop the ones with no recent activity.
_PRUNE_THRESHOLD = 1024


class RateLimiter:
    """Allow at most `max_requests` per `window_seconds` per key (sliding window)."""

    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self._max = max_requests
        self._window = window_seconds
        self._hits: dict[str, list[float]] = {}

    def allow(self, key: str) -> bool:
        """Record a hit for `key`; return False if it is over the limit in the window."""
        now = time.time()
        cutoff = now - self._window
        hits = [t for t in self._hits.get(key, []) if t > cutoff]
        allowed = len(hits) < self._max
        if allowed:
            hits.append(now)
        self._hits[key] = hits
        if len(self._hits) > _PRUNE_THRESHOLD:
            self._hits = {k: v for k, v in self._hits.items() if v and v[-1] > cutoff}
        return allowed

#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""One-time shell tickets: web identity for PTY children (DD-9).

Every web shell runs as the shared ``euler-ws`` uid and ``/proc/<pid>/environ``
is same-uid-readable, so nothing carried in the environment can be a reusable
credential. Identity therefore transfers by a **consumable ticket**:

- the ws service (holding the user's authenticated session cookie) asks the
  auth service to *mint* a ticket bound to ``(email, profile)``;
- the forked PTY child *redeems* it over ``auth.sock`` at startup — redemption
  consumes the ticket and returns the authoritative identity.

Tickets live only in this process's memory, stored **hashed**, expire after
``TICKET_TTL_SECONDS`` (60 s — minting and forking are back-to-back), and are
single-use: replay from a sibling shell's environ is dead on arrival because
the victim's own startup already consumed the ticket.
"""
from __future__ import annotations

__all__ = ['TicketStore']

import secrets
import time
from hashlib import sha256

from solver.web.auth import policy
from solver.web.auth.users import normalize_email


class TicketStore:
    """hash(ticket) → (email, profile, expiry); single-use, short-TTL, in-memory."""

    def __init__(self, ttl_seconds: int = policy.TICKET_TTL_SECONDS) -> None:
        self._ttl = ttl_seconds
        self._tickets: dict[str, tuple[str, str, float]] = {}

    def _sweep(self) -> None:
        now = time.time()
        self._tickets = {key: value for key, value in self._tickets.items() if value[2] > now}

    def mint(self, email: str, profile: str) -> str:
        """Mint a ticket bound to ``(email, profile)``; return the raw token."""
        self._sweep()
        ticket = secrets.token_urlsafe(32)
        key = sha256(ticket.encode()).hexdigest()
        self._tickets[key] = (normalize_email(email), profile, time.time() + self._ttl)
        return ticket

    def redeem(self, ticket: str) -> tuple[str, str] | None:
        """Consume the ticket, returning ``(email, profile)`` — or None if unknown,
        expired, or already redeemed."""
        self._sweep()
        key = sha256(ticket.encode()).hexdigest()
        entry = self._tickets.pop(key, None)
        return (entry[0], entry[1]) if entry is not None else None

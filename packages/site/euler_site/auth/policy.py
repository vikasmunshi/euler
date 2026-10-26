#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Auth policy constants (lifetimes, cookie names, password and OTP rules).

Kept in one place so the server and (where relevant) the browser client agree.
The model these values implement is in docs/web-server-guide.md § Authentication.
"""
from __future__ import annotations

__all__ = ['SESSION_COOKIE', 'SESSION_TTL_SECONDS', 'CHALLENGE_TTL_SECONDS', 'MAX_PENDING_CHALLENGES',
           'MIN_PASSWORD_LENGTH', 'PASSWORD_REQUIRE_CLASSES', 'INVITE_TTL_SECONDS', 'LINK_TOKEN_BYTES',
           'OTP_DIGITS', 'OTP_TTL_SECONDS', 'OTP_MAX_ATTEMPTS', 'OTP_MAX_SENDS',
           'REMEMBER_COOKIE', 'REMEMBER_TTL_SECONDS', 'AUTH_RATE_MAX', 'AUTH_RATE_WINDOW_SECONDS',
           'TICKET_TTL_SECONDS', 'PROFILES', 'RESET_COOLDOWN_SECONDS', 'RESET_DAILY_MAX',
           'MAIL_PER_RECIPIENT_MAX', 'MAIL_PER_RECIPIENT_WINDOW_SECONDS', 'MAIL_DAILY_MAX', 'POW_BITS',
           'POW_TTL_SECONDS']

#: Web-assignable profiles: `admin` is assignable only to a local os-login. The
#: authoritative policy is authorizations.json (see docs/web-server-guide.md
#: § Authorization); this is the invite/validation set for the admin API.
PROFILES: tuple[str, ...] = ('reader', 'contributor', 'maintainer')

#: Name of the short-lived session cookie set on a successful SRP login.
SESSION_COOKIE: str = 'solver_session'
#: Session lifetime — 12 hours (in-memory; a service restart drops sessions).
SESSION_TTL_SECONDS: int = 12 * 3600
#: How long a pending SRP challenge (server ephemeral B) is held between the
#: challenge and verify steps.
CHALLENGE_TTL_SECONDS: int = 120
#: Ceiling on handshakes held at once, across all accounts. Each is keyed by its own id, so
#: starting one never evicts another; this only bounds memory under a flood (oldest go first).
MAX_PENDING_CHALLENGES: int = 4096
#: Minimum password length. The user chooses their password in the browser during
#: registration, so the browser enforces this; the server never sees the password.
MIN_PASSWORD_LENGTH: int = 16
#: Character classes a password must draw from (all four): lower + upper + digit +
#: special. Enforced client-side (mirrored in the registration page) since the
#: server never sees the password; documented here as the single source of truth.
PASSWORD_REQUIRE_CLASSES: tuple[str, ...] = ('lower', 'upper', 'digit', 'special')

#: How long the emailed invite / reset link remains valid — 7 days.
INVITE_TTL_SECONDS: int = 7 * 24 * 3600
#: Entropy (bytes) of the secure invite / reset link token.
LINK_TOKEN_BYTES: int = 32

#: The emailed one-time code proving live mailbox control at completion time.
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

#: Password-reset requests (`/forgot`) per account: after one, another is refused (silently —
#: the page is the same) for this long, and no more than RESET_DAILY_MAX in a day. A new
#: request never invalidates a link already sent, so repeating `/forgot` cannot keep an
#: account's owner from completing a reset.
RESET_COOLDOWN_SECONDS: int = 15 * 60
RESET_DAILY_MAX: int = 4
#: The budget for mail that an unauthenticated request can cause (reset links, OTPs, the
#: invite-request notice): per recipient, and for the whole service per day — well under the
#: relay account's own sending quota, so abuse cannot exhaust it and stop every other mail.
#: Admin invites are not counted.
MAIL_PER_RECIPIENT_MAX: int = 6
MAIL_PER_RECIPIENT_WINDOW_SECONDS: int = 3600
MAIL_DAILY_MAX: int = 150
#: Proof of work in front of the same forms (`auth/pow.py`): zero bits the browser must find —
#: 2^18 hashes on average, about a second — and how long a page's stamp stays solvable.
POW_BITS: int = 18
POW_TTL_SECONDS: int = 10 * 60
#: One-time shell ticket lifetime: minted against a live session at WS
#: attach, redeemed by the PTY child at startup — 60 seconds covers the fork.
TICKET_TTL_SECONDS: int = 60

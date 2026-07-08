#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Pending invite / reset store at ``<state>/pending.json`` (DD-7).

One record per in-flight registration or password reset, keyed by the **hash**
of the emailed link token (the token itself is never stored or logged). The
record walks the DD-7 state machine::

    invited ──(Terms accepted, OTP mailed)──▶ otp_sent ──(OTP matches)──▶ verified
                                                                              │
                                              (salt+verifier posted) consume ─┘

The link token (32 bytes, 7-day TTL, single-use) proves possession of the
invite; the OTP (6 digits, 10-minute TTL, 5 tries) proves *live* control of the
mailbox at completion time. Expired records sweep on every access; ``consume``
deletes the record so a link can complete a registration exactly once.
"""
from __future__ import annotations

__all__ = ['PendingRecord', 'PendingStore', 'generate_token', 'hash_token']

import secrets
import time
from hashlib import sha256
from pathlib import Path
from typing import Any, NamedTuple

from solver.web.auth import policy
from solver.web.auth.storage import load_json, save_json
from solver.web.auth.users import normalize_email


def generate_token() -> str:
    """Return a fresh URL-safe link token (``LINK_TOKEN_BYTES`` of entropy)."""
    return secrets.token_urlsafe(policy.LINK_TOKEN_BYTES)


def hash_token(token: str) -> str:
    """SHA-256 of a token, for storage/lookup (the raw token never persists)."""
    return sha256(token.encode()).hexdigest()


def _generate_otp() -> str:
    """Return a fresh zero-padded numeric OTP of ``OTP_DIGITS`` digits."""
    return str(secrets.randbelow(10 ** policy.OTP_DIGITS)).zfill(policy.OTP_DIGITS)


class PendingRecord(NamedTuple):
    """One in-flight invite/reset (as returned to callers; secrets stay hashed)."""

    email: str
    profile: str
    kind: str            # 'register' | 'reset'
    state: str           # 'invited' | 'otp_sent' | 'verified'
    expiry: float
    terms_version: str
    terms_accepted_at: str
    otp_sends: int

    def summary(self) -> dict[str, Any]:
        """A secret-free view for admin listings."""
        return {'email': self.email, 'profile': self.profile, 'kind': self.kind,
                'state': self.state, 'expires_in_h': max(0, round((self.expiry - time.time()) / 3600, 1))}


class PendingStore:
    """Single-writer store over the pending records, swept on every load."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def _load(self) -> dict[str, dict[str, Any]]:
        now = time.time()
        records = load_json(self._path)
        return {key: rec for key, rec in records.items()
                if isinstance(rec, dict) and float(rec.get('expiry', 0)) > now}

    def _save(self, records: dict[str, dict[str, Any]]) -> None:
        save_json(self._path, records)

    @staticmethod
    def _to_record(raw: dict[str, Any]) -> PendingRecord:
        return PendingRecord(
            email=str(raw.get('email', '')), profile=str(raw.get('profile', 'user')),
            kind=str(raw.get('kind', 'register')), state=str(raw.get('state', 'invited')),
            expiry=float(raw.get('expiry', 0)), terms_version=str(raw.get('terms_version', '')),
            terms_accepted_at=str(raw.get('terms_accepted_at', '')),
            otp_sends=int(raw.get('otp_sends', 0)))

    def mint(self, email: str, profile: str, kind: str) -> str:
        """Create a fresh record (replacing any same-email+kind one); return the link token."""
        records = self._load()
        key_email = normalize_email(email)
        records = {key: rec for key, rec in records.items()
                   if not (rec.get('email') == key_email and rec.get('kind') == kind)}
        token = generate_token()
        records[hash_token(token)] = {
            'email': key_email, 'profile': profile, 'kind': kind, 'state': 'invited',
            'expiry': time.time() + policy.INVITE_TTL_SECONDS,
            'terms_version': '', 'terms_accepted_at': '', 'otp_sends': 0}
        self._save(records)
        return token

    def get(self, token: str) -> PendingRecord | None:
        """Return the live record for a raw link token, or None."""
        raw = self._load().get(hash_token(token))
        return self._to_record(raw) if raw is not None else None

    def accept_terms(self, token: str, terms_version: str, accepted_at: str) -> bool:
        """Record Terms acceptance on the pending record (registration only)."""
        records = self._load()
        raw = records.get(hash_token(token))
        if raw is None:
            return False
        raw['terms_version'] = terms_version
        raw['terms_accepted_at'] = accepted_at
        self._save(records)
        return True

    def issue_otp(self, token: str) -> str | None:
        """Mint and store (hashed) a fresh OTP for the record; None if not allowed.

        Allowed from any pre-``verified`` state while under the send cap; resets the
        attempt counter and moves the record to ``otp_sent``.
        """
        records = self._load()
        raw = records.get(hash_token(token))
        if raw is None or raw.get('state') == 'verified':
            return None
        if int(raw.get('otp_sends', 0)) >= policy.OTP_MAX_SENDS:
            return None
        otp = _generate_otp()
        raw['otp_hash'] = sha256(otp.encode()).hexdigest()
        raw['otp_expiry'] = time.time() + policy.OTP_TTL_SECONDS
        raw['otp_attempts'] = 0
        raw['otp_sends'] = int(raw.get('otp_sends', 0)) + 1
        raw['state'] = 'otp_sent'
        self._save(records)
        return otp

    def verify_otp(self, token: str, otp: str) -> bool:
        """Check the OTP; on success the record becomes ``verified``.

        A wrong try increments the attempt counter; ``OTP_MAX_ATTEMPTS`` failures
        (or expiry) invalidate the OTP — a fresh one must be requested.
        """
        records = self._load()
        raw = records.get(hash_token(token))
        if raw is None or raw.get('state') != 'otp_sent':
            return False
        if float(raw.get('otp_expiry', 0)) <= time.time():
            return False
        attempts = int(raw.get('otp_attempts', 0)) + 1
        raw['otp_attempts'] = attempts
        ok = secrets.compare_digest(str(raw.get('otp_hash', '')), sha256(otp.encode()).hexdigest())
        if ok:
            raw['state'] = 'verified'
            raw.pop('otp_hash', None)
        elif attempts >= policy.OTP_MAX_ATTEMPTS:
            raw.pop('otp_hash', None)          # invalidated: request a fresh OTP
            raw['state'] = 'invited'
        self._save(records)
        return ok

    def consume(self, token: str) -> PendingRecord | None:
        """Pop and return the record iff it is ``verified`` (single-use completion)."""
        records = self._load()
        key = hash_token(token)
        raw = records.get(key)
        if raw is None or raw.get('state') != 'verified':
            return None
        del records[key]
        self._save(records)
        return self._to_record(raw)

    def revoke_email(self, email: str) -> int:
        """Drop every pending record for *email*; return how many were dropped."""
        records = self._load()
        key_email = normalize_email(email)
        keep = {key: rec for key, rec in records.items() if rec.get('email') != key_email}
        dropped = len(records) - len(keep)
        if dropped:
            self._save(keep)
        return dropped

    def all(self) -> list[PendingRecord]:
        """Every live record, sorted by email (for admin listings)."""
        return sorted((self._to_record(raw) for raw in self._load().values()),
                      key=lambda record: record.email)

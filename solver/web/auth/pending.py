#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Persistent pending-registration store: the secure registration / reset links.

Invite-only registration spans two processes: the ``users add`` shell command mints
a secure link token and emails it, while the web server later validates and consumes
it. They therefore cannot share memory — the pending registrations live in a JSON
file (``keys/.pending.json``, gitignored, mode ``0600``) that survives restarts (the
link is valid for 24 h).

Each entry is keyed by the **hash** of the token (never the token itself) and records
the target email, the ``kind`` (``register`` or ``reset``), and an expiry. The token —
a high-entropy random string carried in the emailed URL — is the sole authorisation
to set a password; it is single-use (consumed on completion) and swept on expiry.
"""
from __future__ import annotations

__all__ = ['generate_token', 'PendingStore']

import json
import os
import secrets
import tempfile
import time
from hashlib import sha256
from pathlib import Path
from typing import Any

from solver.web.auth import policy
from solver.web.auth.users import normalize_email


def generate_token() -> str:
    """Return a fresh URL-safe secure link token (``REGISTRATION_TOKEN_BYTES`` of entropy)."""
    return secrets.token_urlsafe(policy.REGISTRATION_TOKEN_BYTES)


def _hash_token(token: str) -> str:
    """SHA-256 of a token, for storage/lookup (the token is never stored raw)."""
    return sha256(token.encode()).hexdigest()


class PendingStore:
    """File-backed pending-registration store, shared between the shell and the server."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def _load(self) -> dict[str, Any]:
        if not self.path.is_file():
            return {'pending': {}}
        data: Any = json.loads(self.path.read_text(encoding='utf-8'))
        if not isinstance(data, dict) or not isinstance(data.get('pending'), dict):
            raise ValueError(f'{self.path} is not a valid pending store')
        return data

    def _save(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=self.path.parent, prefix='.pending-', suffix='.tmp')
        try:
            os.fchmod(fd, 0o600)
            with os.fdopen(fd, 'w', encoding='utf-8') as handle:
                json.dump(data, handle, indent=2)
                handle.write('\n')
            os.replace(tmp, self.path)
        except BaseException:
            os.unlink(tmp)
            raise

    @staticmethod
    def _sweep(pending: dict[str, Any]) -> None:
        """Drop expired entries in place (bounds the file, keeps stale links out)."""
        now = time.time()
        for key in [k for k, e in pending.items() if now >= e.get('expires', 0)]:
            del pending[key]

    def invite(self, email: str, kind: str = 'register') -> str:
        """Mint a fresh secure link token for `email`, replacing any it already has.

        Stores the token's hash with `{email, kind, expires=+24 h}` and returns the raw
        token for the caller to embed in the emailed link. `kind` is 'register' or 'reset'.
        """
        key = normalize_email(email)
        token = generate_token()
        data = self._load()
        pending: dict[str, Any] = data['pending']
        self._sweep(pending)
        # A user has at most one live token; drop any earlier one for this email.
        for existing in [h for h, e in pending.items() if e.get('email') == key]:
            del pending[existing]
        pending[_hash_token(token)] = {
            'email': key,
            'kind': kind,
            'expires': time.time() + policy.REGISTRATION_TTL_SECONDS,
        }
        self._save(data)
        return token

    def resolve(self, token: str) -> tuple[str, str] | None:
        """Return `(email, kind)` for a live token without consuming it, else None.

        The non-consuming check behind ``/register/validate`` (so the page can show the
        target email before the user sets a password). Expired tokens are swept.
        """
        return self._lookup(token, consume=False)

    def consume(self, token: str) -> tuple[str, str] | None:
        """Return `(email, kind)` for a live token and delete it (single-use), else None.

        The authoritative step behind ``/register/complete`` / a password reset.
        """
        return self._lookup(token, consume=True)

    def _lookup(self, token: str, *, consume: bool) -> tuple[str, str] | None:
        if not token:
            return None
        data = self._load()
        pending: dict[str, Any] = data['pending']
        digest = _hash_token(token)
        entry = pending.get(digest)
        if entry is None:
            return None
        if time.time() >= entry['expires']:
            del pending[digest]
            self._save(data)
            return None
        if consume:
            del pending[digest]
            self._save(data)
        return entry['email'], entry['kind']

    def remove_email(self, email: str) -> bool:
        """Drop every pending token for `email`; returns False if there were none."""
        key = normalize_email(email)
        data = self._load()
        pending: dict[str, Any] = data['pending']
        stale = [h for h, e in pending.items() if e.get('email') == key]
        for digest in stale:
            del pending[digest]
        if stale:
            self._save(data)
        return bool(stale)

#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""User store: the SRP verifier database at ``<state>/users.json`` (DD-6).

One entry per registered user, keyed by normalised email, recording only the
SRP ``{salt, verifier}`` (never a password or password-equivalent) plus the
authorization profile, the recorded Terms acceptance (DD-7), and bookkeeping.
A user record exists only once registration **completes** — an outstanding
invite lives in :mod:`solver.web.auth.pending`, not here.

This is **web-auth** material, deliberately separate from ``solver.crypto``
(the git-filter solution encryption): it gates web access and shares no key
material with the encryption master key.

The file is JSON, written atomically at mode ``0600``::

    {
      "version": "srp6a-sha256-2048",
      "users": {
        "user@example.com": {
          "salt": "<hex>", "verifier": "<hex>", "profile": "user",
          "terms_version": "1", "terms_accepted_at": "<iso8601>",
          "created": "<iso8601>", "disabled": false
        }
      }
    }
"""
from __future__ import annotations

__all__ = ['UserRecord', 'UserStore', 'normalize_email']

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, NamedTuple

from solver.web.auth.srp import VERSION, SrpToken
from solver.web.auth.storage import load_json, save_json


def normalize_email(email: str) -> str:
    """Return the canonical store key for an email (trimmed, lowercased)."""
    return email.strip().lower()


def _now() -> str:
    """Current UTC time in ISO-8601, the store's timestamp format."""
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


class UserRecord(NamedTuple):
    """One registered user, as stored (secrets are the SRP salt/verifier only)."""

    email: str
    salt: str            # hex
    verifier: str        # hex
    profile: str
    terms_version: str
    terms_accepted_at: str
    created: str
    disabled: bool

    @property
    def srp_token(self) -> SrpToken:
        """The stored SRP material as the handshake type."""
        return SrpToken(salt=bytes.fromhex(self.salt), verifier=int(self.verifier, 16))

    def summary(self) -> dict[str, Any]:
        """A secret-free view for listings (no salt/verifier)."""
        return {'email': self.email, 'profile': self.profile, 'created': self.created,
                'disabled': self.disabled, 'terms_version': self.terms_version}


class UserStore:
    """The verifier DB: single-writer (the auth service), read per operation."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def _load(self) -> dict[str, dict[str, Any]]:
        users = load_json(self._path).get('users')
        return users if isinstance(users, dict) else {}

    def _save(self, users: dict[str, dict[str, Any]]) -> None:
        save_json(self._path, {'version': VERSION, 'users': users})

    def get(self, email: str) -> UserRecord | None:
        """Return the record for *email*, or None."""
        raw = self._load().get(normalize_email(email))
        if raw is None:
            return None
        return UserRecord(
            email=normalize_email(email), salt=str(raw.get('salt', '')),
            verifier=str(raw.get('verifier', '')), profile=str(raw.get('profile', 'user')),
            terms_version=str(raw.get('terms_version', '')),
            terms_accepted_at=str(raw.get('terms_accepted_at', '')),
            created=str(raw.get('created', '')), disabled=bool(raw.get('disabled', True)))

    def create(self, email: str, salt: str, verifier: str, profile: str,
               terms_version: str, terms_accepted_at: str) -> UserRecord:
        """Create the record at registration completion (DD-7 step 5); enabled."""
        users = self._load()
        key = normalize_email(email)
        users[key] = {'salt': salt, 'verifier': verifier, 'profile': profile,
                      'terms_version': terms_version, 'terms_accepted_at': terms_accepted_at,
                      'created': _now(), 'disabled': False}
        self._save(users)
        record = self.get(key)
        assert record is not None
        return record

    def set_credentials(self, email: str, salt: str, verifier: str) -> bool:
        """Replace the SRP material (password reset); False if the user is unknown."""
        users = self._load()
        key = normalize_email(email)
        if key not in users:
            return False
        users[key]['salt'] = salt
        users[key]['verifier'] = verifier
        self._save(users)
        return True

    def set_enabled(self, email: str, enabled: bool) -> bool:
        """Enable/disable the account; False if the user is unknown."""
        users = self._load()
        key = normalize_email(email)
        if key not in users:
            return False
        users[key]['disabled'] = not enabled
        self._save(users)
        return True

    def remove(self, email: str) -> bool:
        """Delete the account outright; False if the user is unknown."""
        users = self._load()
        if users.pop(normalize_email(email), None) is None:
            return False
        self._save(users)
        return True

    def all(self) -> list[UserRecord]:
        """Every record, sorted by email."""
        records = (self.get(email) for email in sorted(self._load()))
        return [record for record in records if record is not None]

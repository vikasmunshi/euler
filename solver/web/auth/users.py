#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""User store for web authentication: the SRP verifier database at ``keys/.users.json``.

Holds one entry per user, keyed by normalised email, recording only the SRP
``{salt, verifier}`` (never a password or password-equivalent) plus bookkeeping.
This is **web-auth** material, deliberately separate from ``solver.crypto`` — it
gates web access and shares no key material with the solution-encryption master
key.

The file is JSON, written atomically at mode ``0600``:

    {
      "version": "srp6a-sha256-2048",
      "users": {
        "user@example.com": {
          "salt": "<hex>", "verifier": "<hex>",
          "created": "<iso8601>", "disabled": false
        }
      }
    }
"""
from __future__ import annotations

__all__ = ['UserRecord', 'UserStore', 'normalize_email']

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, NamedTuple

from solver.web.auth.srp import VERSION, SrpToken


def normalize_email(email: str) -> str:
    """Return the canonical form of an email used as a lookup key (trimmed, lower-cased)."""
    return email.strip().lower()


class UserRecord(NamedTuple):
    """One user's stored authentication material and bookkeeping.

    An invited-but-not-yet-registered account has no salt/verifier (both None) and
    is disabled; registration sets them and enables the account.
    """

    email: str
    salt: bytes | None
    verifier: int | None
    created: str
    disabled: bool

    @property
    def registered(self) -> bool:
        """True once the user has completed registration (has an SRP verifier)."""
        return self.salt is not None and self.verifier is not None

    @property
    def token(self) -> SrpToken:
        """The SRP token (salt + verifier); only valid for a registered user."""
        if self.salt is None or self.verifier is None:
            raise ValueError(f'{self.email} has not completed registration')
        return SrpToken(salt=self.salt, verifier=self.verifier)


class UserStore:
    """Load/modify/save the SRP verifier database at a JSON file path.

    Every mutating method reads the current file, applies the change, and writes
    the whole file back atomically (temp file in the same directory + ``os.replace``)
    at mode ``0600``, so a crash never leaves a torn file and the secrets are not
    world-readable. Emails are normalised on every access.
    """

    def __init__(self, path: Path) -> None:
        self.path = path

    # -- persistence --------------------------------------------------------
    def _load(self) -> dict[str, Any]:
        """Return the parsed store, or a fresh empty structure when the file is absent."""
        if not self.path.is_file():
            return {'version': VERSION, 'users': {}}
        data: Any = json.loads(self.path.read_text(encoding='utf-8'))
        if not isinstance(data, dict) or not isinstance(data.get('users'), dict):
            raise ValueError(f'{self.path} is not a valid user store')
        return data

    def _save(self, data: dict[str, Any]) -> None:
        """Write `data` back atomically at mode 0600, creating the parent directory."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=self.path.parent, prefix='.users-', suffix='.tmp')
        try:
            os.fchmod(fd, 0o600)
            with os.fdopen(fd, 'w', encoding='utf-8') as handle:
                json.dump(data, handle, indent=2, ensure_ascii=False)
                handle.write('\n')
            os.replace(tmp, self.path)
        except BaseException:
            os.unlink(tmp)
            raise

    @staticmethod
    def _to_record(email: str, entry: dict[str, Any]) -> UserRecord:
        """Build a :class:`UserRecord` from a stored JSON entry (salt/verifier optional)."""
        salt_hex = entry.get('salt')
        verifier_hex = entry.get('verifier')
        return UserRecord(
            email=email,
            salt=bytes.fromhex(salt_hex) if salt_hex else None,
            verifier=int(verifier_hex, 16) if verifier_hex else None,
            created=entry['created'],
            disabled=bool(entry.get('disabled', False)),
        )

    # -- queries ------------------------------------------------------------
    def get(self, email: str) -> UserRecord | None:
        """Return the record for `email`, or None if there is no such user."""
        key = normalize_email(email)
        entry = self._load()['users'].get(key)
        return self._to_record(key, entry) if entry is not None else None

    def is_active(self, email: str) -> bool:
        """Return True if the user exists, has registered, and is not disabled."""
        record = self.get(email)
        return record is not None and record.registered and not record.disabled

    def emails(self) -> list[str]:
        """Return all stored emails, sorted."""
        return sorted(self._load()['users'].keys())

    def records(self) -> list[UserRecord]:
        """Return all user records, sorted by email."""
        users: dict[str, Any] = self._load()['users']
        return [self._to_record(email, users[email]) for email in sorted(users)]

    # -- mutations ----------------------------------------------------------
    def invite(self, email: str) -> UserRecord:
        """Create a disabled, password-less invited account (no-op if it already exists).

        Returns the record (existing or new). Registration later sets the verifier and
        enables it; callers should refuse to re-invite an already-registered user.
        """
        key = normalize_email(email)
        data = self._load()
        if key not in data['users']:
            data['users'][key] = {'created': datetime.now(timezone.utc).isoformat(), 'disabled': True}
            self._save(data)
        return self._to_record(key, data['users'][key])

    def register(self, email: str, token: SrpToken) -> UserRecord:
        """Store the user's SRP verifier and enable the account (registration complete).

        Creates the account if absent, otherwise preserves its `created`; always clears
        `disabled` so the user can log in.
        """
        key = normalize_email(email)
        data = self._load()
        existing: dict[str, Any] = data['users'].get(key, {})
        entry = {
            'salt': token.salt.hex(),
            'verifier': format(token.verifier, 'x'),
            'created': existing.get('created') or datetime.now(timezone.utc).isoformat(),
            'disabled': False,
        }
        data['users'][key] = entry
        self._save(data)
        return self._to_record(key, entry)

    def set_disabled(self, email: str, disabled: bool) -> bool:
        """Set the user's disabled flag; returns False if the user does not exist."""
        key = normalize_email(email)
        data = self._load()
        entry = data['users'].get(key)
        if entry is None:
            return False
        entry['disabled'] = disabled
        self._save(data)
        return True

    def remove(self, email: str) -> bool:
        """Delete the user; returns False if there was no such user."""
        key = normalize_email(email)
        data = self._load()
        if key not in data['users']:
            return False
        del data['users'][key]
        self._save(data)
        return True

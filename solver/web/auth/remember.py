#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Persistent "remember me" tokens (selector\\:validator, rotated on use).

A remember-me cookie is ``<selector>:<validator>``. The server stores, per
selector, the user's email, an HMAC of the validator (keyed by a persistent server
secret), and an expiry — in ``keys/remember.json`` (gitignored, ``0600``) so logins
survive a server restart even though in-memory sessions do not.

On each use the validator is **rotated** (one-time-use): a fresh validator replaces
the old one and a new cookie is issued. A selector presented with a wrong validator
is treated as theft/forgery and deleted. (A rare race — two truly parallel requests
that both lack a session — can invalidate a live token; that fails secure, forcing a
re-login.) Only ``keys/.session-secret`` is new key material here, and it is web-auth
only — separate from the encryption master key.
"""
from __future__ import annotations

__all__ = ['RememberStore', 'load_or_create_secret']

import hmac
import json
import os
import secrets
import tempfile
import time
from hashlib import sha256
from pathlib import Path
from typing import Any


def load_or_create_secret(path: Path) -> bytes:
    """Return the 32-byte server secret at `path`, creating it (mode 0600) if absent."""
    if path.is_file():
        return path.read_bytes()
    path.parent.mkdir(parents=True, exist_ok=True)
    secret = secrets.token_bytes(32)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'wb') as handle:
        handle.write(secret)
    return secret


class RememberStore:
    """File-backed selector→(email, HMAC(validator), expiry) map with rotation."""

    def __init__(self, path: Path, secret: bytes, ttl_seconds: int) -> None:
        self.path = path
        self._secret = secret
        self._ttl = ttl_seconds

    def _load(self) -> dict[str, Any]:
        if not self.path.is_file():
            return {'tokens': {}}
        data: Any = json.loads(self.path.read_text(encoding='utf-8'))
        if not isinstance(data, dict) or not isinstance(data.get('tokens'), dict):
            raise ValueError(f'{self.path} is not a valid remember store')
        return data

    def _save(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=self.path.parent, prefix='.remember-', suffix='.tmp')
        try:
            os.fchmod(fd, 0o600)
            with os.fdopen(fd, 'w', encoding='utf-8') as handle:
                json.dump(data, handle, indent=2)
                handle.write('\n')
            os.replace(tmp, self.path)
        except BaseException:
            os.unlink(tmp)
            raise

    def _mac(self, validator: str) -> str:
        """Keyed HMAC-SHA256 of a validator, as stored/compared (never the raw validator)."""
        return hmac.new(self._secret, validator.encode(), sha256).hexdigest()

    def issue(self, email: str) -> str:
        """Mint a remember token for `email`; return the `selector:validator` cookie value."""
        selector = secrets.token_urlsafe(16)
        validator = secrets.token_urlsafe(32)
        data = self._load()
        data['tokens'][selector] = {
            'email': email,
            'validator': self._mac(validator),
            'expires': time.time() + self._ttl,
        }
        self._save(data)
        return f'{selector}:{validator}'

    def validate_and_rotate(self, cookie: str | None) -> tuple[str, str] | None:
        """Validate a remember cookie; on success rotate it and return (email, new_cookie).

        Returns None for a missing/expired/forged cookie. A wrong validator for a known
        selector deletes that selector (theft response).
        """
        if not cookie or ':' not in cookie:
            return None
        selector, _, validator = cookie.partition(':')
        data = self._load()
        entry = data['tokens'].get(selector)
        if entry is None:
            return None
        if time.time() >= entry['expires']:
            del data['tokens'][selector]
            self._save(data)
            return None
        if not secrets.compare_digest(entry['validator'], self._mac(validator)):
            del data['tokens'][selector]        # wrong validator for a live selector → revoke
            self._save(data)
            return None
        new_validator = secrets.token_urlsafe(32)
        entry['validator'] = self._mac(new_validator)
        entry['expires'] = time.time() + self._ttl
        self._save(data)
        return entry['email'], f'{selector}:{new_validator}'

    def revoke(self, cookie: str | None) -> None:
        """Delete the token identified by a cookie's selector (used on logout)."""
        if not cookie or ':' not in cookie:
            return
        selector = cookie.partition(':')[0]
        data = self._load()
        if selector in data['tokens']:
            del data['tokens'][selector]
            self._save(data)

    def revoke_all(self, email: str) -> None:
        """Delete every remember token for `email` (used on password change)."""
        data = self._load()
        keep = {sel: entry for sel, entry in data['tokens'].items() if entry.get('email') != email}
        if len(keep) != len(data['tokens']):
            data['tokens'] = keep
            self._save(data)

    @property
    def ttl_seconds(self) -> int:
        """The remember-me lifetime, for setting the cookie max-age."""
        return self._ttl

#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""One-time passwords and the shared pending-registration store.

Invite-only registration spans two processes: the `users add` shell command seeds
a pending registration and emails the OTP, while the web server verifies it. They
therefore cannot share memory — the pending registrations live in a JSON file
(``keys/pending.json``, gitignored, mode ``0600``), each holding a salted hash of
the OTP (never the OTP itself), an expiry, and an attempt counter.
"""
from __future__ import annotations

__all__ = ['generate_otp', 'PendingStore']

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


def generate_otp() -> str:
    """Return a fresh numeric OTP of the configured length (leading zeros kept)."""
    return ''.join(secrets.choice('0123456789') for _ in range(policy.OTP_LENGTH))


def _hash_otp(otp: str, salt: bytes) -> str:
    """Salted SHA-256 of an OTP, for storage/comparison (the OTP is never stored raw)."""
    return sha256(salt + otp.encode()).hexdigest()


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

    def invite(self, email: str, otp: str) -> None:
        """Seed (or replace) a pending registration for `email` with a fresh OTP."""
        key = normalize_email(email)
        salt = secrets.token_bytes(16)
        data = self._load()
        data['pending'][key] = {
            'salt': salt.hex(),
            'hash': _hash_otp(otp, salt),
            'expires': time.time() + policy.OTP_TTL_SECONDS,
            'attempts': 0,
        }
        self._save(data)

    def check(self, email: str, otp: str, *, consume: bool) -> bool:
        """Validate `otp` for `email`.

        Returns True only for a live, unlocked, matching OTP. A wrong OTP increments
        the attempt counter (locking the registration after `OTP_MAX_ATTEMPTS`); an
        expired one is dropped. With `consume=True` a successful match deletes the
        pending entry (the authoritative step in `/register/complete`); `consume=False`
        leaves it in place (the `/register/verify` pre-check).
        """
        key = normalize_email(email)
        data = self._load()
        entry = data['pending'].get(key)
        if entry is None:
            return False
        if time.time() >= entry['expires']:
            del data['pending'][key]
            self._save(data)
            return False
        if entry['attempts'] >= policy.OTP_MAX_ATTEMPTS:
            return False
        if not secrets.compare_digest(entry['hash'], _hash_otp(otp, bytes.fromhex(entry['salt']))):
            entry['attempts'] += 1
            self._save(data)
            return False
        if consume:
            del data['pending'][key]
            self._save(data)
        return True

    def remove(self, email: str) -> bool:
        """Drop a pending registration; returns False if there was none."""
        key = normalize_email(email)
        data = self._load()
        if key not in data['pending']:
            return False
        del data['pending'][key]
        self._save(data)
        return True

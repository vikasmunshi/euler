#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Persistent "remember me" tokens at ``<state>/remember.json``.

A remember-me cookie is ``<selector>:<validator>``. Per selector the store
keeps the user's email, an HMAC of the validator (keyed by the persistent
32-byte ``<state>/session-secret``, created on first start), and an expiry —
so logins survive a service restart even though sessions are in-memory.

On each use the validator **rotates** (one-time-use): a fresh cookie replaces
the old one. A selector presented with a wrong validator is treated as theft or
forgery and deleted — failing secure to a re-login.
"""
from __future__ import annotations

__all__ = ['RememberStore', 'load_or_create_secret']

import hmac
import os
import secrets
import time
from hashlib import sha256
from pathlib import Path
from typing import Any

from solver.web.auth import policy
from solver.web.auth.storage import load_json, save_json
from solver.web.auth.users import normalize_email


def load_or_create_secret(path: Path) -> bytes:
    """Return the 32-byte server secret at *path*, creating it (mode 0600) if absent."""
    if path.is_file():
        return path.read_bytes()
    path.parent.mkdir(parents=True, exist_ok=True)
    secret = secrets.token_bytes(32)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'wb') as handle:
        handle.write(secret)
    return secret


class RememberStore:
    """Selector → (email, HMAC(validator), expiry), rotated on every redemption."""

    def __init__(self, path: Path, secret: bytes) -> None:
        self._path = path
        self._secret = secret

    def _mac(self, validator: str) -> str:
        return hmac.new(self._secret, validator.encode(), sha256).hexdigest()

    def _load(self) -> dict[str, dict[str, Any]]:
        now = time.time()
        records = load_json(self._path)
        return {key: rec for key, rec in records.items()
                if isinstance(rec, dict) and float(rec.get('expiry', 0)) > now}

    def issue(self, email: str) -> str:
        """Mint a fresh token for *email*; return the cookie value ``selector:validator``."""
        records = self._load()
        selector = secrets.token_urlsafe(9)
        validator = secrets.token_urlsafe(32)
        records[selector] = {'email': normalize_email(email), 'validator': self._mac(validator),
                             'expiry': time.time() + policy.REMEMBER_TTL_SECONDS}
        save_json(self._path, records)
        return f'{selector}:{validator}'

    def redeem(self, cookie: str) -> tuple[str, str] | None:
        """Validate and rotate; return ``(email, new_cookie)`` or None.

        A known selector with a wrong validator is deleted (stolen/forged token);
        the legitimate holder simply logs in again.
        """
        selector, _, validator = cookie.partition(':')
        if not selector or not validator:
            return None
        records = self._load()
        record = records.get(selector)
        if record is None:
            return None
        del records[selector]                  # one-time-use: old token dies either way
        if not hmac.compare_digest(str(record.get('validator', '')), self._mac(validator)):
            save_json(self._path, records)     # theft signal — drop it, fail secure
            return None
        email = str(record.get('email', ''))
        new_selector = secrets.token_urlsafe(9)
        new_validator = secrets.token_urlsafe(32)
        records[new_selector] = {'email': email, 'validator': self._mac(new_validator),
                                 'expiry': time.time() + policy.REMEMBER_TTL_SECONDS}
        save_json(self._path, records)
        return email, f'{new_selector}:{new_validator}'

    def revoke(self, cookie: str) -> None:
        """Drop the token in *cookie* (logout)."""
        selector = cookie.partition(':')[0]
        records = self._load()
        if records.pop(selector, None) is not None:
            save_json(self._path, records)

    def revoke_email(self, email: str) -> int:
        """Drop every token for *email* (disable/remove); return how many."""
        records = self._load()
        key_email = normalize_email(email)
        keep = {key: rec for key, rec in records.items() if rec.get('email') != key_email}
        dropped = len(records) - len(keep)
        if dropped:
            save_json(self._path, keep)
        return dropped

#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Prospective-collaborator invite requests at ``<state>/requests.json``.

The intake queue behind the login page's "Request an invite" form. A visitor
with **no account** submits their name, email and remarks; the record lands here
and the operator reviews it (folded into ``users list``) and works through it with
``users process-requests`` — accept (invite + provision), ignore (leave), or
dismiss (drop). Submitting creates **zero** authorization state — it is a request,
not a grant; only the sudo admin path (``users process-requests`` → ``users add``)
mints an invite and provisions an instance.

This store is the **system of record** for requests: the owner-notification
email (:meth:`AuthService.notify_invite_request`) is a best-effort nudge layered
on top, so a wedged mail relay loses a notification, never the request.

Guard rails, since the form is unauthenticated:

- every field is length-capped and control-char-stripped on the way in
  (:func:`sanitize`);
- records are deduped by normalised email (a resubmit updates in place, refreshes
  the TTL and bumps ``submissions``);
- a **global** cap of :data:`MAX_REQUESTS` distinct emails and a **hard per-IP**
  sub-cap of :data:`MAX_PER_IP` bound how much one source can queue — the client
  IP is stored only as a keyed hash (:data:`_secret`), never in the clear;
- records expire :data:`REQUEST_TTL_SECONDS` after their last submission and sweep
  on every access, so an unworked queue does not grow without bound.

The public handler answers the same generic message whether the request stored,
deduped, or was dropped (cap or TTL) — no capacity or membership signal.
"""
from __future__ import annotations

__all__ = ['MAX_PER_IP', 'MAX_REQUESTS', 'NAME_MAX', 'REMARKS_MAX', 'REQUEST_TTL_SECONDS',
           'RequestRecord', 'RequestStore', 'sanitize']

import hmac
import time
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, NamedTuple

from solver.web.auth.storage import load_json, save_json
from solver.web.auth.users import normalize_email

#: Distinct emails the queue holds before further *new* requests are dropped (a
#: resubmit from an already-queued email always updates in place). Bounds the
#: disk an unauthenticated form can consume.
MAX_REQUESTS: int = 500
#: Hard per-IP sub-cap: at most this many *live* queued requests may share one
#: source IP. Stops a single client filling the queue with distinct emails even
#: while under the global cap (the rate limiter only bounds burst, not standing total).
MAX_PER_IP: int = 50
#: A queued request lives this long after its last submission, then sweeps — an
#: unworked request is stale after a month and the person can simply re-request.
REQUEST_TTL_SECONDS: int = 30 * 24 * 3600
#: Length caps for the free-text fields (characters, after sanitising).
NAME_MAX: int = 100
REMARKS_MAX: int = 1000


def _now_iso() -> str:
    """Current UTC time in ISO-8601 (the store's display timestamp)."""
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def sanitize(text: str, max_len: int, *, allow_newlines: bool = False) -> str:
    """Strip control characters, cap length, and trim — for untrusted free text.

    Drops C0/C1 control characters (so a name or remark cannot smuggle newlines
    into a notification-mail header or control codes into the ``users list``
    terminal listing); tabs become spaces. With *allow_newlines* the record keeps
    its line breaks (remarks), which stay in the mail **body** where they are
    inert. The cap is applied last, so the stored value never exceeds *max_len*.
    """
    out: list[str] = []
    for ch in text:
        if ch == '\n':
            out.append(ch if allow_newlines else ' ')
        elif ch == '\t':
            out.append(' ')
        elif ch < ' ' or ch == '\x7f' or '\x80' <= ch <= '\x9f':
            continue
        else:
            out.append(ch)
    return ''.join(out).strip()[:max_len]


class RequestRecord(NamedTuple):
    """One prospective collaborator's invite request (the display view)."""

    name: str
    email: str
    remarks: str
    created: str            # first-seen ISO-8601
    updated: str            # last-resubmit ISO-8601
    submissions: int        # how many times this email has submitted

    def summary(self) -> dict[str, Any]:
        """A view for the admin listing (already sanitised at rest; no IP, no expiry)."""
        return {'name': self.name, 'email': self.email, 'remarks': self.remarks,
                'created': self.created, 'updated': self.updated, 'submissions': self.submissions}


class RequestStore:
    """Single-writer store over the invite-request queue, keyed by normalised email.

    *secret* keys the HMAC used to fingerprint the submitter IP for the per-IP cap,
    so the raw address never lands on disk (the file is euler-auth-private, but the
    IP still need not be retained in the clear).
    """

    def __init__(self, path: Path, secret: bytes) -> None:
        self._path = path
        self._secret = secret

    def _ip_hash(self, client_ip: str) -> str:
        """A stable, non-reversible fingerprint of *client_ip* for the per-IP cap."""
        return hmac.new(self._secret, client_ip.encode(), sha256).hexdigest()[:16]

    def _load(self) -> dict[str, dict[str, Any]]:
        """Live records only — expired ones (TTL) are swept on every access."""
        now = time.time()
        records = load_json(self._path)
        return {key: rec for key, rec in records.items()
                if isinstance(rec, dict) and float(rec.get('expiry', 0)) > now}

    def _save(self, records: dict[str, dict[str, Any]]) -> None:
        save_json(self._path, records)

    @staticmethod
    def _to_record(raw: dict[str, Any]) -> RequestRecord:
        return RequestRecord(
            name=str(raw.get('name', '')), email=str(raw.get('email', '')),
            remarks=str(raw.get('remarks', '')), created=str(raw.get('created', '')),
            updated=str(raw.get('updated', '')), submissions=int(raw.get('submissions', 1)))

    def submit(self, name: str, email: str, remarks: str, client_ip: str) -> bool:
        """Queue (or refresh) a request; return False on a bad email or a hit cap.

        A resubmit from an already-queued email updates its name/remarks, refreshes
        the TTL and bumps ``submissions`` in place — it never counts against either
        cap. A brand-new email is dropped (False) once the global queue is full
        (:data:`MAX_REQUESTS`) or its source IP already holds :data:`MAX_PER_IP` live
        requests. Fields are sanitised here so every caller stores clean values.
        """
        key = normalize_email(email)
        if '@' not in key:
            return False
        records = self._load()
        now = time.time()
        clean_name = sanitize(name, NAME_MAX)
        clean_remarks = sanitize(remarks, REMARKS_MAX, allow_newlines=True)
        ip_hash = self._ip_hash(client_ip)
        existing = records.get(key)
        if existing is not None:
            existing.update(name=clean_name, remarks=clean_remarks, updated=_now_iso(),
                            expiry=now + REQUEST_TTL_SECONDS, ip_hash=ip_hash,
                            submissions=int(existing.get('submissions', 1)) + 1)
        else:
            if len(records) >= MAX_REQUESTS:
                return False
            if sum(1 for rec in records.values() if rec.get('ip_hash') == ip_hash) >= MAX_PER_IP:
                return False
            iso = _now_iso()
            records[key] = {'name': clean_name, 'email': key, 'remarks': clean_remarks,
                            'created': iso, 'updated': iso, 'submissions': 1,
                            'ip_hash': ip_hash, 'expiry': now + REQUEST_TTL_SECONDS}
        self._save(records)
        return True

    def dismiss(self, email: str) -> bool:
        """Drop the request for *email*; return whether one was there."""
        records = self._load()
        if records.pop(normalize_email(email), None) is None:
            return False
        self._save(records)
        return True

    def all(self) -> list[RequestRecord]:
        """Every live request, oldest first (for the admin listing)."""
        return sorted((self._to_record(raw) for raw in self._load().values()),
                      key=lambda record: record.created)

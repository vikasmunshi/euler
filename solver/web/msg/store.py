#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The message spool at `<state>/messages.json` — messages and read-state.

One record per **message**, never per recipient. A broadcast is therefore a single
record naming N recipients rather than N copies: "everyone" costs one write,
read-state stays per-person, and a collaborator provisioned after a notice was sent is
simply not in it — which is the correct behaviour, not an omission.

**Every message stands on its own — there are no replies.** This is not an email or chat
replacement: it is how a *command* tells somebody something they must act on, and the act
is always on one message. Threading bought conversation nobody was having, and cost a
second place for content to hide: an answer buried in a reply is invisible to anything
reading the message it answers.

Every party to a thread appears in `recipients`, keyed by **box**
(:func:`solver.web.msg.identity.box_of`), carrying that box's read timestamp:

- the **author** is present and already read — they wrote it;
- an **inbound** message (user → staff) additionally names the staff boxes at submit
  time, and :meth:`MessageStore.threads_for` shows *every* inbound message to *any*
  staff reader regardless, adding them lazily when they read. So a maintainer promoted
  after the fact still sees the queue, rather than only what was addressed to the
  roster as it stood.

Bounded like the invite-request queue it resembles: a global cap, a per-author standing
cap, field length caps, and a TTL swept on every access, so an unworked spool cannot
grow without limit. Bodies are stored as **plaintext** — sanitised on the way in and
rendered through Jinja autoescape — so no markup ever survives to be interpreted.

Single-writer by construction: one `euler-msg` process owns the file.
"""
from __future__ import annotations

__all__ = ['BODY_MAX', 'MAX_PER_AUTHOR', 'MAX_THREADS', 'MessageStore',
           'SUBJECT_MAX', 'THREAD_TTL_SECONDS', 'Thread']

import secrets
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, NamedTuple

from solver.web.store import load_json, sanitize, save_json

#: Threads the spool holds before further *new* ones are refused.
MAX_THREADS: int = 2000
#: Live threads one author may hold open at once — bounds a single chatty sender
#: without the rate limiter's burst-only view.
MAX_PER_AUTHOR: int = 50
#: A thread lives this long after its last activity, then sweeps. Long enough that an
#: answered question stays readable for a season, short enough to bound the file.
THREAD_TTL_SECONDS: int = 90 * 24 * 3600
#: Length caps for the free-text fields (characters, after sanitising).
SUBJECT_MAX: int = 200
BODY_MAX: int = 8000

#: What a thread is: a question to staff, or a notice from them.
Kind = Literal['inbound', 'notice']


def _now_iso() -> str:
    """Current UTC time in ISO-8601 (the store's display timestamp)."""
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


class Thread(NamedTuple):
    """One thread as its readers see it (already sanitised at rest)."""

    id: str
    kind: str
    author: str                     # box key of whoever started it
    subject: str
    body: str
    recipients: list[str]           # box keys party to the thread
    created: str
    updated: str
    unread: bool                    # for the box that asked

    def summary(self, *, author_name: str = '') -> dict[str, Any]:
        """A view for a reader. *author_name* carries the display identity.

        The store holds box keys only — it never needs an e-mail address to route a
        message — so the caller resolves the name through the policy view and passes it
        in. An unresolvable box degrades to itself rather than dropping the message.
        """
        return {'id': self.id, 'kind': self.kind, 'author': self.author,
                'author_name': author_name or self.author, 'subject': self.subject,
                'body': self.body, 'recipients': self.recipients,
                'created': self.created, 'updated': self.updated, 'unread': self.unread}


class MessageStore:
    """Single-writer store over the message spool, keyed by thread id."""

    def __init__(self, path: Path) -> None:
        self._path = path

    # ── persistence ────────────────────────────────────────────────────────────────

    def _load(self) -> dict[str, dict[str, Any]]:
        """Live threads only — expired ones (TTL) are swept on every access."""
        now = time.time()
        records = load_json(self._path)
        return {key: rec for key, rec in records.items()
                if isinstance(rec, dict) and float(rec.get('expiry', 0)) > now}

    def _save(self, records: dict[str, dict[str, Any]]) -> None:
        save_json(self._path, records)

    # ── reading ────────────────────────────────────────────────────────────────────

    @staticmethod
    def _visible_to(raw: dict[str, Any], box: str, *, staff: bool) -> bool:
        """Whether *box* may see this thread.

        Three ways in: it is addressed to them, they wrote it, or it is an inbound
        thread and they are staff (the queue is shared — see the module docstring).
        """
        if box in (raw.get('recipients') or {}) or raw.get('author') == box:
            return True
        return staff and raw.get('kind') == 'inbound'

    @staticmethod
    def _unread_for(raw: dict[str, Any], box: str) -> bool:
        """Whether *box* has yet to read this thread's latest activity.

        A box absent from `recipients` has never read it — which is exactly the
        newly-promoted maintainer looking at an older queue thread.
        """
        recipients: dict[str, Any] = raw.get('recipients') or {}
        entry = recipients.get(box)
        if entry is None:
            return True
        return not (isinstance(entry, dict) and entry.get('read'))

    def _to_thread(self, raw: dict[str, Any], box: str) -> Thread:
        return Thread(
            id=str(raw.get('id', '')), kind=str(raw.get('kind', 'inbound')),
            author=str(raw.get('author', '')), subject=str(raw.get('subject', '')),
            body=str(raw.get('body', '')),
            recipients=sorted(raw.get('recipients') or {}),
            created=str(raw.get('created', '')), updated=str(raw.get('updated', '')),
            unread=self._unread_for(raw, box))

    def threads_for(self, box: str, *, staff: bool = False) -> list[Thread]:
        """Every thread *box* may read, newest activity first."""
        records = self._load()
        visible = [raw for raw in records.values() if self._visible_to(raw, box, staff=staff)]
        return sorted((self._to_thread(raw, box) for raw in visible),
                      key=lambda thread: thread.updated, reverse=True)

    def thread(self, thread_id: str, box: str, *, staff: bool = False) -> Thread | None:
        """One thread by id, or None when absent or not *box*'s to read."""
        raw = self._load().get(thread_id)
        if raw is None or not self._visible_to(raw, box, staff=staff):
            return None
        return self._to_thread(raw, box)

    def unread_count(self, box: str, *, staff: bool = False) -> int:
        """How many visible threads *box* has not read — the header badge's number."""
        return sum(1 for thread in self.threads_for(box, staff=staff) if thread.unread)

    def inbound(self, box: str = '') -> list[Thread]:
        """Every inbound thread, oldest first — the staff queue, as a work list.

        *box* is whoever is looking, so each thread's `unread` is that reader's own
        state. Without it every row would read as unread (an empty box is in no
        thread's recipients), which is exactly the marker being useless.
        """
        records = self._load()
        threads = [self._to_thread(raw, box) for raw in records.values()
                   if raw.get('kind') == 'inbound']
        return sorted(threads, key=lambda thread: thread.created)

    # ── writing ────────────────────────────────────────────────────────────────────

    def _create(self, kind: Kind, author: str, subject: str, body: str,
                recipients: list[str]) -> str | None:
        """Write a new thread; return its id, or None if a cap or a bad field refuses it.

        The author is a recipient of their own thread, already read: it is the read-state
        a reply resets, which is how an answer reaches the person who asked.
        """
        clean_subject = sanitize(subject, SUBJECT_MAX)
        clean_body = sanitize(body, BODY_MAX, allow_newlines=True)
        if not clean_subject or not clean_body or not recipients:
            return None
        records = self._load()
        if len(records) >= MAX_THREADS:
            return None
        mine = sum(1 for raw in records.values() if raw.get('author') == author)
        if mine >= MAX_PER_AUTHOR:
            return None
        now, iso = time.time(), _now_iso()
        thread_id = secrets.token_hex(8)
        entries: dict[str, dict[str, str | None]] = {author: {'read': iso}}
        for box in recipients:
            entries.setdefault(box, {'read': None})
        records[thread_id] = {'id': thread_id, 'kind': kind, 'author': author,
                              'subject': clean_subject, 'body': clean_body,
                              'recipients': entries, 'created': iso, 'updated': iso,
                              'expiry': now + THREAD_TTL_SECONDS}
        self._save(records)
        return thread_id

    def submit(self, author: str, subject: str, body: str, staff: list[str]) -> str | None:
        """Queue a user→staff question; return the thread id or None (cap / bad field)."""
        return self._create('inbound', author, subject, body, staff)

    def notice(self, author: str, subject: str, body: str, recipients: list[str]) -> str | None:
        """Send a staff notice to *recipients*; return the thread id or None."""
        return self._create('notice', author, subject, body, recipients)

    def mark_read(self, thread_id: str, box: str, *, staff: bool = False) -> bool:
        """Mark *thread_id* read by *box*, joining the thread if they were not in it."""
        records = self._load()
        raw = records.get(thread_id)
        if raw is None or not self._visible_to(raw, box, staff=staff):
            return False
        recipients: dict[str, Any] = raw.get('recipients') or {}
        recipients[box] = {'read': _now_iso()}
        raw['recipients'] = recipients
        self._save(records)                 # `updated` is activity, not attention
        return True

    def drop(self, thread_id: str) -> bool:
        """Delete a thread outright (the staff queue's dismiss); True if one was there."""
        records = self._load()
        if records.pop(thread_id, None) is None:
            return False
        self._save(records)
        return True

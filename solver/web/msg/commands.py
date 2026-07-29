#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The ``msg`` shell command: read and write the message spool.

Registered at the **reader** floor — the terminal is the front door for every rung, and
a new invitee's first need is often to ask a question. The staff verbs (``queue``,
``notice``, ``dismiss``) check the caller's profile against
:data:`~solver.web.msg.identity.STAFF_FLOOR` inside the command, the same shape
``users list`` uses to self-scope for a non-admin: one command, one registration, and
the ladder enforced where the verb is.

**Two channels, one renderer.** Which plane answers — the web shell's direct
``msg.sock``, or the operator's ``sudo`` fallback — is :mod:`solver.web.msg.client`'s
problem, not this module's. Both come back as the same JSON, and everything below
renders it identically; a ``None`` from the client means neither plane answered, which
:func:`_unreachable` says once for every verb.

That client is shared: ``user-authorize <thread-id>`` reads and answers a key-request
thread through the same two planes (:mod:`solver.crypto.keys`), which is why the call
lives beside the spool rather than inside this command.
"""
from __future__ import annotations

__all__ = ['msg']

from typing import Any, Literal

from solver.auth.subject import rank
from solver.config import config
from solver.core import osc
from solver.shell import console, register
from solver.web.msg.client import call as _call
from solver.web.msg import KEY_ISSUE_SUBJECT
from solver.web.msg.identity import STAFF_FLOOR


def _unreachable() -> int:
    """The one message for "no spool answered", on either plane."""
    console.print('[error]error:[/error] the message service is not reachable '
                  '(is euler-msg.service running?)')
    return 1


def _is_staff() -> bool:
    """Whether this shell's subject is at or above the staff floor."""
    return rank(config.subject.profile) >= rank(STAFF_FLOOR)


def _refuse_below_staff(verb: str) -> int:
    console.print(f'[error]error:[/error] msg {verb} requires {STAFF_FLOOR} '
                  f'(you are {config.subject.profile})')
    return 77


# ── rendering ───────────────────────────────────────────────────────────────────────

def _when(stamp: str) -> str:
    """An ISO-8601 timestamp trimmed to the minute — the row has to fit one line."""
    return stamp[:16].replace('T', ' ')


def _print_thread_line(thread: dict[str, Any], *, show_kind: bool = True) -> None:
    """One line per thread: unread marker, id, when, who, subject."""
    mark = '[accent]●[/accent]' if thread.get('unread') else ' '
    kind = f'{thread.get("kind", ""):7} ' if show_kind else ''
    replies = len(thread.get('replies') or [])
    tail = f' [muted](+{replies})[/muted]' if replies else ''
    console.print(f'  {mark} [accent]{thread.get("id", "")}[/accent] '
                  f'[muted]{_when(str(thread.get("updated", "")))}[/muted] {kind}'
                  f'{str(thread.get("author_name", ""))[:18]:18} {thread.get("subject", "")}{tail}')


def _print_thread(thread: dict[str, Any]) -> None:
    """One message in full — there is nothing else to it."""
    console.print(f'\n[accent]{thread.get("subject", "")}[/accent]  '
                  f'[muted]({thread.get("kind", "")} · {thread.get("id", "")})[/muted]')
    console.print(f'[muted]from[/muted] {thread.get("author_name", "")}  '
                  f'[muted]{_when(str(thread.get("created", "")))}[/muted]')
    for line in str(thread.get('body') or '').splitlines():
        console.print(f'  {line}')


# ── verbs ───────────────────────────────────────────────────────────────────────────

def _list() -> int:
    """Every message this caller may read, newest first."""
    result = _call('mailbox')
    if result is None:
        return _unreachable()
    status, data = result
    if status != 200 or not isinstance(data, dict):
        console.print(f'[error]error:[/error] {status} {data}')
        return 1
    threads = data.get('threads') or []
    if not threads:
        console.print('[muted]no messages[/muted]')
        return 0
    unread = int(data.get('unread', 0))
    console.print(f'[accent]{len(threads)}[/accent] thread(s), '
                  f'[accent]{unread}[/accent] unread — read one with `msg read <id>`')
    for thread in threads:
        _print_thread_line(thread)
    return 0


def _read(thread_id: str) -> int:
    """Show one thread and mark it read."""
    result = _call('thread', thread_id=thread_id)
    if result is None:
        return _unreachable()
    status, data = result
    if status != 200 or not isinstance(data, dict):
        console.print(f'[error]error:[/error] {status} {data}')
        return 1
    _print_thread(data)
    _call('read', thread_id=thread_id)      # attention, not activity — failure is harmless
    osc.messages_changed()                  # the unread count just dropped
    return 0


def _send(subject: str, body: str) -> int:
    """Ask staff something."""
    result = _call('send', body={'subject': subject, 'body': body})
    if result is None:
        return _unreachable()
    status, data = result
    if status != 201 or not isinstance(data, dict):
        console.print(f'[error]error:[/error] {status} {data}')
        return 1
    console.print(f'[success]sent[/success] [muted]({data.get("id")})[/muted] — '
                  'staff will see it in their queue')
    osc.messages_changed()
    return 0


def _queue() -> int:
    """The inbound queue as a work list (staff)."""
    result = _call('queue')
    if result is None:
        return _unreachable()
    status, data = result
    if status != 200 or not isinstance(data, dict):
        console.print(f'[error]error:[/error] {status} {data}')
        return 1
    queue = data.get('queue') or []
    if not queue:
        console.print('[muted]the inbound queue is empty[/muted]')
        return 0
    console.print(f'[accent]{len(queue)}[/accent] inbound thread(s), oldest first — '
                  'work them with `user-authorize <id>` or `msg notice`, drop with '
                  '`msg dismiss <id>`')
    for thread in queue:
        _print_thread_line(thread, show_kind=False)
    return 0


def _notice(to: str, subject: str, body: str) -> int:
    """Send a notice to named recipients, or to everyone with ``--all``."""
    targets: str | list[str] = '*' if to == '*' else [part.strip() for part in to.split(',') if part.strip()]
    if not targets:
        console.print('[error]error:[/error] msg notice needs `to=<email[,email…]>` or `--all`')
        return 2
    result = _call('notice', body={'to': targets, 'subject': subject, 'body': body})
    if result is None:
        return _unreachable()
    status, data = result
    if status != 201 or not isinstance(data, dict):
        console.print(f'[error]error:[/error] {status} {data}')
        return 1
    count = data.get('recipients', 0)
    console.print(f'[success]notice sent[/success] to [accent]{count}[/accent] '
                  f'recipient(s) [muted]({data.get("id")})[/muted]')
    osc.messages_changed()
    return 0


def _save(thread_id: str) -> int:
    """Write the master key delivered in *thread_id* to this machine's enc-key file.

    The receiving half of key distribution. `user-authorize` (or `key-rekey`) wraps the master
    key to your public key and sends it; this takes it. Nothing else can write that file, and
    nothing writes it without proving the payload first:

    - the thread's **subject** must be the key-issue one, so no other message can be mined
      for something that looks like key material;
    - the payload must **unwrap with your private key** and its `verify` must decrypt to the
      known text. Only then does it replace what you have.

    That order matters. The file it overwrites may be the only thing standing between this
    machine and the whole private tree, so a bad or mistargeted payload has to fail *before*
    the write, not be discovered after it.
    """
    from solver.crypto.keys import save_issued_key
    result = _call('thread', thread_id=thread_id)
    if result is None:
        return _unreachable()
    status, data = result
    if status != 200 or not isinstance(data, dict):
        console.print(f'[error]error:[/error] {status} {data}')
        return 1
    # An issued key is always its own message: with no replies there is nowhere else for it
    # to be, and one subject to check.
    if not str(data.get('subject', '')).startswith(KEY_ISSUE_SUBJECT):
        console.print(f'[error]error:[/error] message [accent]{thread_id}[/accent] does not carry '
                      'a master key — `msg save` writes key material and nothing else')
        return 1
    if not save_issued_key(str(data.get('body', ''))):
        return 1
    _call('read', thread_id=thread_id)      # worked, so it is read
    osc.messages_changed()
    return 0


def _dismiss(thread_id: str) -> int:
    """Drop a worked thread from the spool (staff)."""
    result = _call('dismiss', thread_id=thread_id)
    if result is None:
        return _unreachable()
    status, data = result
    if status != 200:
        console.print(f'[error]error:[/error] {status} {data}')
        return 1
    console.print(f'[success]dismissed[/success] [muted]({thread_id})[/muted]')
    osc.messages_changed()
    return 0


@register(requires='reader', aliases=('messages',),
          help_text='Read and send messages: your threads, questions to staff, staff notices.')
def msg(action: Literal['list', 'read', 'save', 'send', 'queue', 'notice',
                        'dismiss'] = 'list',
        thread: str = '', subject: str = '', body: str = '',
        to: str = '', all_users: bool = False) -> int:
    """Read and write the message spool (web-server-guide § Messaging).

    Every message has staff (``maintainer``+) at one end: you can ask them something,
    they can answer, and they can send notices. There is deliberately no user-to-user
    messaging. Delivery is asynchronous — the spool holds the thread until you read it.

    Args:
        action:    list (your threads, newest first), read (one thread, and mark it
                   read), save (take the master key a maintainer issued you, writing it
                   to your enc-key file), send (ask staff a question), queue (STAFF: the
                   inbound work list), notice (STAFF: send to named recipients or
                   everyone), dismiss (STAFF: drop a worked message).
        thread:    the message id (read / save / dismiss).
        subject:   the subject line (send / notice).
        body:      the message text (send / notice).
        to:        comma-separated recipient identities for a notice.
        all_users: send the notice to every mapped identity (``--all-users``).
    """
    if action == 'list':
        return _list()

    if action == 'queue':
        return _queue() if _is_staff() else _refuse_below_staff('queue')

    if action in ('read', 'save', 'dismiss') and not thread:
        console.print(f'[error]error:[/error] msg {action} requires a message id '
                      '(see `msg list`)')
        return 2

    if action == 'read':
        return _read(thread)

    if action == 'save':
        return _save(thread)

    if action == 'dismiss':
        return _dismiss(thread) if _is_staff() else _refuse_below_staff('dismiss')

    if not subject or not body:
        console.print(f'[error]error:[/error] msg {action} requires subject="…" and body="…"')
        return 2

    if action == 'send':
        return _send(subject, body)

    # notice (staff): named recipients, or every mapped identity with --all-users.
    if not _is_staff():
        return _refuse_below_staff('notice')
    return _notice('*' if all_users else to, subject, body)

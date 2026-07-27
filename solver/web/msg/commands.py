#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The ``msg`` shell command: read and write the message spool.

Registered at the **reader** floor — the terminal is the front door for every rung, and
a new invitee's first need is often to ask a question. The staff verbs (``queue``,
``notice``, ``dismiss``) check the caller's profile against
:data:`~solver.web.msg.identity.STAFF_FLOOR` inside the command, the same shape
``users list`` uses to self-scope for a non-admin: one command, one registration, and
the ladder enforced where the verb is.

**Two channels, one renderer.** A web shell's uid is in ``euler-web``, so its PTY child
dials ``msg.sock`` directly — the kernel proves who it is and no credential is involved.
The operator's terminal uid is not in that group by design, so it goes through
``sudo python -m solver.web.msg.admin`` (:mod:`solver.web.msg.admin`), which injects the
invoking identity and proxies the same call. Both come back as the same JSON, and
everything below renders it identically.

The channel is chosen by *what this process can reach*, not by a flag: the direct socket
is tried first and the sudo path is the fallback, so a collaborator never sees a sudo
prompt and the operator never needs to remember which plane they are on.
"""
from __future__ import annotations

__all__ = ['msg']

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Literal

from solver.auth.subject import rank
from solver.config import config
from solver.core import osc
from solver.shell import console, register
from solver.web.msg import ADMIN_SOCKET_ENV, DEFAULT_ADMIN_SOCKET, DEFAULT_MSG_SOCKET, MSG_SOCKET_ENV
from solver.web.msg.identity import STAFF_FLOOR
from solver.web.unixhttp import request

#: The scoped env file the admin CLI reads its token from — its presence is what tells
#: us a spool is deployed here at all, so a plain dev checkout never prompts for sudo.
_MSG_ENV = '/etc/euler/msg.env'

#: Logical operation → (method, public path, admin path). The two planes expose the same
#: verbs under different prefixes; this table is the only place that knows both.
_OPS: dict[str, tuple[str, str, str]] = {
    'mailbox': ('GET', '/messages', '/admin/messages'),
    'thread': ('GET', '/messages/{id}', '/admin/threads/{id}'),
    'send': ('POST', '/messages', '/admin/messages'),
    'reply': ('POST', '/messages/{id}/reply', '/admin/threads/{id}/reply'),
    'read': ('POST', '/messages/{id}/read', '/admin/threads/{id}/read'),
    'queue': ('GET', '/staff/queue', '/admin/queue'),
    'notice': ('POST', '/staff/notice', '/admin/notice'),
    'dismiss': ('DELETE', '/staff/queue/{id}', '/admin/threads/{id}'),
}


def _socket_path() -> str:
    """The public spool socket (env-overridable, for tests and dev runs)."""
    return os.environ.get(MSG_SOCKET_ENV, DEFAULT_MSG_SOCKET)


def _sudo_plane_present() -> bool:
    """Whether a spool admin plane exists to sudo into.

    Checked before spending a sudo prompt: on a plain dev checkout with no web stack
    there is nothing behind the fallback, and asking for a password only to fail is
    worse than saying the service is not reachable.
    """
    return (Path(os.environ.get('EULER_MSG_ENV', _MSG_ENV)).exists()
            or Path(os.environ.get(ADMIN_SOCKET_ENV, DEFAULT_ADMIN_SOCKET)).exists())


def _direct(method: str, path: str, body: dict[str, Any] | None) -> tuple[int, Any] | None:
    """Call the spool over ``msg.sock``; None when this uid cannot reach it.

    An ``OSError`` here is the *expected* outcome for the operator's own uid (not in
    ``euler-web``) and for a host with no spool deployed — it is the signal to try the
    sudo plane, not an error to report.
    """
    try:
        return request(_socket_path(), method, path, body=body, timeout=15.0)
    except OSError:
        return None


def _via_sudo(method: str, path: str, body: dict[str, Any] | None) -> tuple[int, Any] | None:
    """Call the spool through the sudo admin CLI; None when that fails outright.

    The body goes in on **stdin**, never in ``argv`` — a message in the process table
    would be readable by every uid on the host.
    """
    argv = ['sudo', sys.executable, '-m', 'solver.web.msg.admin', 'api', method, path]
    try:
        proc = subprocess.run(argv, input=json.dumps(body or {}), stdout=subprocess.PIPE,
                              text=True, check=False)
    except (OSError, KeyboardInterrupt) as exc:
        console.print(f'[error]error:[/error] could not run the message admin CLI ({exc})')
        return None
    if proc.returncode != 0:
        return None                         # the CLI already reported on stderr
    try:
        envelope = json.loads(proc.stdout or '{}')
        return int(envelope['status']), envelope['body']
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        console.print('[error]error:[/error] malformed reply from the message admin plane')
        return None


def _call(op: str, *, thread_id: str = '', body: dict[str, Any] | None = None) -> tuple[int, Any] | None:
    """Run *op* on whichever plane this process can reach; None when neither answered."""
    method, public, admin = _OPS[op]
    direct = _direct(method, public.format(id=thread_id), body)
    if direct is not None:
        return direct
    if not _sudo_plane_present():
        return None
    return _via_sudo(method, admin.format(id=thread_id), body)


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
    """One thread in full: the opening message, then every reply in order."""
    console.print(f'\n[accent]{thread.get("subject", "")}[/accent]  '
                  f'[muted]({thread.get("kind", "")} · {thread.get("id", "")})[/muted]')
    console.print(f'[muted]from[/muted] {thread.get("author_name", "")}  '
                  f'[muted]{_when(str(thread.get("created", "")))}[/muted]')
    for line in str(thread.get('body') or '').splitlines():
        console.print(f'  {line}')
    for reply in thread.get('replies') or []:
        console.print(f'\n[muted]reply from[/muted] {reply.get("author_name", "")}  '
                      f'[muted]{_when(str(reply.get("at", "")))}[/muted]')
        for line in str(reply.get('body') or '').splitlines():
            console.print(f'  {line}')
    console.print()


# ── verbs ───────────────────────────────────────────────────────────────────────────

def _list() -> int:
    """Every thread this caller may read, newest activity first."""
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


def _reply(thread_id: str, body: str) -> int:
    """Reply on a thread you are party to."""
    result = _call('reply', thread_id=thread_id, body={'body': body})
    if result is None:
        return _unreachable()
    status, data = result
    if status != 200:
        console.print(f'[error]error:[/error] {status} {data}')
        return 1
    console.print(f'[success]replied[/success] [muted]({thread_id})[/muted]')
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
                  'answer with `msg reply <id> "…"`, drop with `msg dismiss <id>`')
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
def msg(action: Literal['list', 'read', 'send', 'reply', 'queue', 'notice', 'dismiss'] = 'list',
        thread: str = '', subject: str = '', body: str = '',
        to: str = '', all_users: bool = False) -> int:
    """Read and write the message spool (web-server-guide § Messaging).

    Every message has staff (``maintainer``+) at one end: you can ask them something,
    they can answer, and they can send notices. There is deliberately no user-to-user
    messaging. Delivery is asynchronous — the spool holds the thread until you read it.

    Args:
        action:    list (your threads, newest first), read (one thread, and mark it
                   read), send (ask staff a question), reply (answer on a thread you
                   are party to), queue (STAFF: the inbound work list), notice (STAFF:
                   send to named recipients or everyone), dismiss (STAFF: drop a
                   worked thread).
        thread:    the thread id (read / reply / dismiss).
        subject:   the subject line (send / notice).
        body:      the message text (send / reply / notice).
        to:        comma-separated recipient identities for a notice.
        all_users: send the notice to every mapped identity (``--all-users``).
    """
    if action == 'list':
        return _list()

    if action == 'queue':
        return _queue() if _is_staff() else _refuse_below_staff('queue')

    if action in ('read', 'dismiss', 'reply') and not thread:
        console.print(f'[error]error:[/error] msg {action} requires a thread id '
                      '(see `msg list`)')
        return 2

    if action == 'read':
        return _read(thread)

    if action == 'dismiss':
        return _dismiss(thread) if _is_staff() else _refuse_below_staff('dismiss')

    if action == 'reply':
        if not body:
            console.print('[error]error:[/error] msg reply requires body="…"')
            return 2
        return _reply(thread, body)

    if not subject or not body:
        console.print(f'[error]error:[/error] msg {action} requires subject="…" and body="…"')
        return 2

    if action == 'send':
        return _send(subject, body)

    # notice (staff): named recipients, or every mapped identity with --all-users.
    if not _is_staff():
        return _refuse_below_staff('notice')
    return _notice('*' if all_users else to, subject, body)

#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The shell tier's client for the message spool: one call, whichever plane answers.

Extracted from :mod:`solver.web.msg.commands`, which was its only caller until
``user-authorize <thread-id>`` needed to read and answer a thread from
:mod:`solver.crypto.keys` (web-server-guide § Messaging). A command that wants the spool
now asks here rather than re-deriving the two-plane dance — or, worse, reaching into the
``msg`` command's privates.

**Two channels, one call.** A web shell's uid is in ``euler-web``, so it dials
``msg.sock`` directly and the kernel proves who it is. The operator's terminal uid is
deliberately *not* in that group, so it falls back to
``sudo python -m solver.web.msg.admin``, which injects the invoking identity and proxies
the same call. The channel is chosen by *what this process can reach*, never by a flag:
a collaborator never sees a sudo prompt, and the operator never has to remember which
plane they are on.

**Silent.** Failures are logged, not printed: this is called from inside other commands,
which own what the user reads. :func:`call` returns ``None`` for "neither plane
answered", and the caller says so in its own words.

Stdlib-only (via :mod:`solver.web.unixhttp`), like the rest of the shell-facing half of
this package.
"""
from __future__ import annotations

__all__ = ['OPS', 'call', 'sudo_plane_present']

import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from solver.web.msg import ADMIN_SOCKET_ENV, DEFAULT_ADMIN_SOCKET, DEFAULT_MSG_SOCKET, MSG_SOCKET_ENV
from solver.web.unixhttp import request

log = logging.getLogger('solver.msg')

#: The scoped env file the admin CLI reads its token from — its presence is what tells
#: us a spool is deployed here at all, so a plain dev checkout never prompts for sudo.
_MSG_ENV = '/etc/euler/msg.env'

#: Logical operation → (method, public path, admin path). The two planes expose the same
#: verbs under different prefixes; this table is the only place that knows both.
OPS: dict[str, tuple[str, str, str]] = {
    'mailbox': ('GET', '/messages', '/admin/messages'),
    'thread': ('GET', '/messages/{id}', '/admin/threads/{id}'),
    'send': ('POST', '/messages', '/admin/messages'),
    'read': ('POST', '/messages/{id}/read', '/admin/threads/{id}/read'),
    'queue': ('GET', '/staff/queue', '/admin/queue'),
    'notice': ('POST', '/staff/notice', '/admin/notice'),
    'dismiss': ('DELETE', '/staff/queue/{id}', '/admin/threads/{id}'),
}


def _socket_path() -> str:
    """The public spool socket (env-overridable, for tests and dev runs)."""
    return os.environ.get(MSG_SOCKET_ENV, DEFAULT_MSG_SOCKET)


def sudo_plane_present() -> bool:
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
        log.debug('message admin CLI could not be run (%s)', exc)
        return None
    if proc.returncode != 0:
        return None                         # the CLI already reported on stderr
    try:
        envelope = json.loads(proc.stdout or '{}')
        return int(envelope['status']), envelope['body']
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        log.debug('malformed reply from the message admin plane: %r', proc.stdout)
        return None


def call(op: str, *, thread_id: str = '', body: dict[str, Any] | None = None) -> tuple[int, Any] | None:
    """Run *op* on whichever plane this process can reach; None when neither answered."""
    method, public, admin = OPS[op]
    direct = _direct(method, public.format(id=thread_id), body)
    if direct is not None:
        return direct
    if not sudo_plane_present():
        return None
    return _via_sudo(method, admin.format(id=thread_id), body)

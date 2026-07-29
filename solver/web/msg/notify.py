#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Send a message **from a command** — the message layer's actual purpose.

Both directions live here: :func:`notify_staff` files a request from inside another
command, and :func:`read_thread` / :func:`answer_thread` let the command that *works*
that request read it and answer it (``user-authorize <thread-id>``).

The spool is not a mailbox for people to write in; it is the mechanism by which a
command tells staff something they have to act on. The founding case is ``user``: it
mints a keypair, and the public key is useless until an admin runs ``user-authorize``
on it. Until now the account page said *"copy your public key to the admin and wait"*
with nothing behind "and wait" — the collaborator had to find the operator out of band.
Now the command itself files the request.

Two properties every caller depends on:

- **Best-effort, never raising.** A wedged or undeployed spool must not fail the act
  that was trying to report itself. ``user`` still mints the keypair; the operator just
  learns about it the next time they look rather than from a message. This is the same
  posture as the auth service's invite-request notification (§4): the *thing itself* is
  the system of record, the message is a nudge on top.
- **No console output.** These fire inside another command's flow, which owns what the
  user reads. A failure is logged, not printed — a collaborator who just minted a key
  does not need a message-service diagnostic in the middle of their key output.

Stdlib-only (via :mod:`solver.web.unixhttp`), so a command can call it in a base install
with no aiohttp — the shell tier has no web dependencies.
"""
from __future__ import annotations

__all__ = ['answer_thread', 'notify_staff', 'read_thread']

import logging
import os
from typing import Any

from solver.web.msg import DEFAULT_MSG_SOCKET, MSG_SOCKET_ENV
from solver.web.msg.client import call
from solver.web.unixhttp import request

log = logging.getLogger('solver.msg')

#: Cap on the wait. A command is blocked on this, so a slow spool must cost a beat and
#: then be given up on — not hold a keypair mint open.
_TIMEOUT: float = 5.0


def notify_staff(subject: str, body: str) -> bool:
    """Queue a message to staff (``maintainer``+); return whether it was accepted.

    Callers may ignore the result — it is returned for the few that want to say
    "reported" versus "tell them yourself". Reaches the spool the same way the shell
    command does, so the sender is this process's uid via ``SO_PEERCRED`` and there is
    no identity to pass or forge.
    """
    socket_path = os.environ.get(MSG_SOCKET_ENV, DEFAULT_MSG_SOCKET)
    try:
        status, _body = request(socket_path, 'POST', '/messages',
                                body={'subject': subject, 'body': body}, timeout=_TIMEOUT)
    except (OSError, TimeoutError) as exc:
        # The common case on a plain dev checkout: no spool is deployed. Debug, not
        # warning — there is nothing wrong and nothing for anyone to do.
        log.debug('message spool unreachable (%s); not notifying staff', exc)
        return False
    if status != 201:
        log.warning('staff notification refused (%s)', status)
        return False
    return True


def read_thread(thread_id: str) -> dict[str, Any] | None:
    """One thread as staff see it, or None when it cannot be read.

    The other half of :func:`notify_staff`: a command that *files* a request has a
    counterpart command that *works* it, and the worker needs the thread back. Used by
    ``user-authorize <thread-id>``, which takes the key-authorization request the
    collaborator's ``user`` command filed and turns it into a grant.

    Unlike :func:`notify_staff` this goes through :mod:`solver.web.msg.client`, so it
    reaches the spool from the operator's own terminal (which is deliberately outside
    ``euler-web``) via the sudo plane. That is the right trade for this direction: the
    caller is a maintainer who asked for this, so a sudo prompt is expected, where a
    notification firing inside someone's key mint must never prompt for anything.
    """
    result = call('thread', thread_id=thread_id)
    if result is None:
        return None
    status, data = result
    return data if status == 200 and isinstance(data, dict) else None


def answer_thread(thread_id: str, body: str) -> bool:
    """Reply on *thread_id* and mark it read; return whether the reply landed.

    The pair is the point, and the pair is deliberate: replying tells the collaborator
    the thing they were waiting for (their message chip lights up), and marking read
    takes it off the staff unread count without **dismissing** it — the thread stays in
    the spool as the record of what was granted, for the collaborator to read and for
    ``msg dismiss`` to close explicitly when the operator wants it gone.

    Best-effort in the same sense as :func:`notify_staff`: the grant itself is already
    written to ``enc-key.json``, so a spool that refuses the reply must not fail the
    authorization — the caller reports which of the two happened.
    """
    result = call('reply', thread_id=thread_id, body={'body': body})
    replied = result is not None and result[0] == 200
    if not replied:
        log.warning('reply to thread %s refused (%s)', thread_id, result and result[0])
    call('read', thread_id=thread_id)       # attention, not activity — failure is harmless
    return replied

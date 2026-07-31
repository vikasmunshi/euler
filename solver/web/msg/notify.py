#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Send a message **from a command** — the message layer's actual purpose.

Both directions live here: :func:`notify_staff` files a request from inside another
command, :func:`read_thread` lets the command that *works* it read it, and
:func:`notify_user` sends the result as **its own message** — there are no replies, and a
grant that hid inside one would be invisible to everything reading the request.

The spool is not a mailbox for people to write in; it is the mechanism by which a
command tells staff something they have to act on. The founding case is `user`: it
mints a keypair, and the public key is useless until an admin runs `user-authorize`
on it. Until now the account page said *"copy your public key to the admin and wait"*
with nothing behind "and wait" — the collaborator had to find the operator out of band.
Now the command itself files the request.

Two properties every caller depends on:

- **Best-effort, never raising.** A wedged or undeployed spool must not fail the act
  that was trying to report itself. `user` still mints the keypair; the operator just
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

__all__ = ['dismiss_by_subject', 'dismiss_thread', 'notify_staff', 'notify_user', 'read_thread']

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
    """Queue a message to staff (`maintainer`+); return whether it was accepted.

    Callers may ignore the result — it is returned for the few that want to say
    "reported" versus "tell them yourself". Reaches the spool the same way the shell
    command does, so the sender is this process's uid via `SO_PEERCRED` and there is
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


def notify_user(identity: str, subject: str, body: str) -> bool:
    """Send *identity* a staff notice; return whether it was accepted.

    The other direction from :func:`notify_staff`, and the delivery half of key issuance:
    `user-authorize` answers a request on its own thread, but `key-rekey` has no thread to
    answer — it is telling people something they never asked for — so it opens one.

    Goes through :mod:`solver.web.msg.client`, so it reaches the spool from the operator's
    terminal (deliberately outside `euler-web`) via the sudo plane. A rotation is already
    an interactive admin act, so a sudo prompt here surprises nobody.
    """
    result = call('notice', body={'to': [identity], 'subject': subject, 'body': body})
    accepted = result is not None and result[0] == 201
    if not accepted:
        log.warning('notice to %s refused (%s)', identity, result and result[0])
    return accepted


def read_thread(thread_id: str) -> dict[str, Any] | None:
    """One thread as staff see it, or None when it cannot be read.

    The other half of :func:`notify_staff`: a command that *files* a request has a
    counterpart command that *works* it, and the worker needs the thread back. Used by
    `user-authorize <thread-id>`, which takes the key-authorization request the
    collaborator's `user` command filed and turns it into a grant.

    Unlike :func:`notify_staff` this goes through :mod:`solver.web.msg.client`, so it
    reaches the spool from the operator's own terminal (which is deliberately outside
    `euler-web`) via the sudo plane. That is the right trade for this direction: the
    caller is a maintainer who asked for this, so a sudo prompt is expected, where a
    notification firing inside someone's key mint must never prompt for anything.
    """
    result = call('thread', thread_id=thread_id)
    if result is None:
        return None
    status, data = result
    return data if status == 200 and isinstance(data, dict) else None


def dismiss_thread(thread_id: str) -> bool:
    """Drop a message that has been acted on; return whether it went.

    An act that leaves its own instruction lying around is half an act — the request a key
    was issued for is worked, and a queue that keeps worked requests is a queue nobody
    trusts. Best-effort, like everything else here: the grant is already delivered, so a
    spool that refuses must not fail it.
    """
    result = call('dismiss', thread_id=thread_id)
    dismissed = result is not None and result[0] == 200
    if not dismissed:
        log.warning('could not dismiss %s (%s)', thread_id, result and result[0])
    return dismissed


def dismiss_by_subject(subject: str) -> int:
    """Drop every visible thread whose subject is exactly *subject*; return how many went.

    :func:`dismiss_thread` for the act that has **no thread id to work with**. A command
    that files a notice can hand the id to whoever works it; `git-push` cannot — the act
    that answers its notice is a merge, which works the pull requests *GitHub* knows and
    never reads the spool. So the notice carries the correlation in its subject
    (:data:`~solver.web.msg.PR_REVIEW_SUBJECT` + the branch), and the merge dismisses by
    that subject once the branch has landed. The branch is load-bearing twice over: it is
    also what :func:`~solver.core.git.merge_pr_for_branch` resolves into the request number
    when the act is taken from the chip.

    An exact match, never a prefix: the prefix names a *kind* of message and would sweep
    every waiting pull request the moment one of them merged.

    Best-effort like the rest of this module — the act is already done, and a spool that
    cannot be reached must not fail it. Zero is therefore both "nothing matched" and
    "no spool answered"; callers report what they did, not what the spool was doing.
    """
    result = call('mailbox')
    if result is None or result[0] != 200 or not isinstance(result[1], dict):
        log.debug('mailbox unreadable; nothing dismissed for %r', subject)
        return 0
    threads: Any = result[1].get('threads') or []
    ids = [str(thread.get('id', '')) for thread in threads
           if isinstance(thread, dict) and str(thread.get('subject', '')) == subject]
    return sum(1 for thread_id in ids if thread_id and dismiss_thread(thread_id))

#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The message spool: user↔staff threads, on its own uid (web-server-guide § Messaging).

Three flows, and only three — any user → staff (`maintainer`+), staff → named
users, staff → everyone. There is **no user↔user leg**: every message has staff at
one end, which makes this a helpdesk plus an announcements board rather than chat.

Why a separate service rather than routes on the auth service: the spool holds
attacker-authored free text by design, and auth holds the SRP verifier database, the
session table and the ticket mint. The same rule that keeps the Gmail credentials in
`euler-smtp` applies in reverse — an untrusted-input surface lives *away* from the
secrets it has no business near. So this package imports **nothing** from
:mod:`euler_site.auth`; the shared unix-socket client and JSON store live at
:mod:`euler_site.unixhttp` / :mod:`euler_site.store` instead.

It is reachable only over its unix sockets, never routed by Caddy, and authenticates
by `SO_PEERCRED` against `authorizations.json` — so it needs no session cookie, no
bearer token on the hot path, and no contact with the auth service at all.

Import discipline, as in :mod:`euler_site.auth`: this `__init__` and the
`commands` module stay **stdlib-only importable** (the shell imports them in a base
install with no aiohttp); `app`/`store`/`identity`/`__main__` are the service
side and run from the deployed `/opt/euler` venv.
"""
from __future__ import annotations

__all__ = ['KEY_ISSUE_SUBJECT',
           'KEY_REQUEST_SUBJECT', 'KEY_SHARE_SUBJECT', 'PR_REVIEW_SUBJECT',
           'UNREGISTERED_SUBJECT', 'verb_for']

# The subjects are the contract between the commands that file notices and the spool's readers;
# they live with the solver's notices (stdlib-only), which both sides import.
from solver.core.notices import (KEY_ISSUE_SUBJECT, KEY_REQUEST_SUBJECT, KEY_SHARE_SUBJECT,
                                 PR_REVIEW_SUBJECT, UNREGISTERED_SUBJECT)


def verb_for(subject: str, *, is_staff: bool, is_own: bool, from_staff: bool) -> str:
    """What a message is asking to have done: `save` | `reconstruct` | `authorize` | `merge` | `read`.

    **The one rule, in one place.** `msg act <id>` runs it and the header's message chip
    labels its rows with it (:mod:`euler_webshell.user.msg_api`), so the two cannot drift — the
    chip can never name an act the command would not take, because the command re-derives
    it from the same subject at the moment it runs.

    Every message stands on its own (there are no replies), so the subject is enough to say
    what one is for. The rules, decided against the constants the *filing* commands match on:

    - a **key issued to you** is `save`: the thing to do with a key is take it;
    - **half a key** is `reconstruct`: the same thing to do, one step longer — it is completed
      with the half your clone already carries before there is a key to take.
      Both only for a message **staff** sent (a `notice` — the spool lets nobody below the
      staff floor create one). Anyone may write to staff, and the subject is theirs to
      choose, so an inbound "key" is prose: taking it would install a key its sender holds;
    - somebody else's **key request**, seen by staff, is `authorize` — the grant they are
      waiting for. Not your own: what you await on that one is the reply, not a self-grant;
    - a **pull request**, seen by staff, is `merge`. No `is_own` exclusion here, unlike a key
      request: the owner pushes and merges their own branch as a matter of course;
    - everything else is `read`, which is also what a rung below staff gets on the two staff
      acts. That is the honest answer rather than a refusal — a reader offered a grant they
      can never make is worse off than one shown prose.

    Args:
        subject: The message's subject line, as the spool stored it.
        is_staff: Whether the caller is at :data:`~euler_webshell.msg.identity.STAFF_FLOOR`.
        is_own: Whether the caller wrote this message.
        from_staff: Whether staff sent it — a `notice` thread, as the spool records it.
    """
    # The share subject first: it is not a prefix of the issue one, but the two read alike,
    # and the order says which is which without anybody having to check that.
    if subject.startswith(KEY_SHARE_SUBJECT):
        return 'reconstruct' if from_staff else 'read'
    if subject.startswith(KEY_ISSUE_SUBJECT):
        return 'save' if from_staff else 'read'
    if subject.startswith(KEY_REQUEST_SUBJECT) and is_staff and not is_own:
        return 'authorize'
    if subject.startswith(PR_REVIEW_SUBJECT) and is_staff:
        return 'merge'
    return 'read'


# The socket paths and the variables that override them are settings, and live in the one
# table: `[msg]` in `packages/solver/solver/config/env.conf`, read through `solver.config.env.load_spec`.
# The reasoning that picks those values belongs beside them and is recorded there — the
# public socket joins the shared `/run/euler` fabric (`euler-web`-only, which the
# operator's own uid deliberately is not), while the admin socket sits in this service's
# **own** runtime dir, `/run/euler-msg`, rather than in euler-auth-private `/run/euler-adm`.

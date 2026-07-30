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
:mod:`solver.web.auth`; the shared unix-socket client and JSON store live at
:mod:`solver.web.unixhttp` / :mod:`solver.web.store` instead.

It is reachable only over its unix sockets, never routed by Caddy, and authenticates
by `SO_PEERCRED` against `authorizations.json` — so it needs no session cookie, no
bearer token on the hot path, and no contact with the auth service at all.

Import discipline, as in :mod:`solver.web.auth`: this `__init__` and the
`commands` module stay **stdlib-only importable** (the shell imports them in a base
install with no aiohttp); `app`/`store`/`identity`/`__main__` are the service
side and run from the deployed `/opt/euler` venv.
"""
from __future__ import annotations

__all__ = ['ADMIN_SOCKET_ENV', 'DEFAULT_ADMIN_SOCKET', 'DEFAULT_MSG_SOCKET', 'KEY_ISSUE_SUBJECT',
           'KEY_REQUEST_SUBJECT', 'MSG_SOCKET_ENV', 'PR_REVIEW_SUBJECT', 'UNREGISTERED_SUBJECT',
           'verb_for']

#: The subject a key-authorization request is filed under — the one message *kind* the
#: spool carries that another command can work. It lives here, with the socket paths,
#: because it is a wire convention between three parties that must not drift: `user`
#: files it (:mod:`solver.crypto.keys`), `user-authorize <id>` requires it before reading
#: a public key out of a body, and :func:`verb_for` reads it to make `msg act` on such a
#: message *be* that grant. Anything else in the spool is prose for a person to read.
KEY_REQUEST_SUBJECT: str = 'Key authorization request from '

#: The subject a *granted* key is delivered under — `user-authorize`'s reply and
#: `key-rekey`'s re-issue. `msg act` requires it before it will write anything to the
#: enc-key file: the payload is the whole of a holder's key material, so the one message
#: kind that can overwrite it is named, not guessed at from the presence of some JSON.
KEY_ISSUE_SUBJECT: str = 'Master key for '

#: The subject a pull request is announced under — `git-push` files it the moment it opens
#: one, and :func:`verb_for` reads it to make `msg act` on such a message the merge itself.
#: A wire convention like the two above, and for the same reason: the chip must never name
#: an act the command would not take. Unlike a key message the body is not a payload — the
#: reviewer's verb is `gh-merge merge`, which reads the open pull requests from GitHub — so
#: this is a pure nudge, and the **branch in the subject is the correlation**: the merge has
#: no thread id in hand, and dismisses the notice by matching this subject once the branch
#: has landed (`solver.core.git._dismiss_pr_notice`). Which is why the branch is part of the
#: subject rather than only of the body.
PR_REVIEW_SUBJECT: str = 'Pull request ready for review: '

#: The subject `summary` files under when the progress page disagrees with what is recorded
#: as solved: a problem `mark` set solved whose answer projecteuler.net has never been given
#: — so it is solved here and not there. Prose for a person to read (the verb is a plain
#: `msg read`), named here so it sits with the other command-filed subjects rather than
#: being invented at the call site.
UNREGISTERED_SUBJECT: str = 'Answer not registered for '


def verb_for(subject: str, *, is_staff: bool, is_own: bool) -> str:
    """What a message is asking to have done: `save` | `authorize` | `merge` | `read`.

    **The one rule, in one place.** `msg act <id>` runs it and the header's message chip
    labels its rows with it (:mod:`solver.web.user.msg_api`), so the two cannot drift — the
    chip can never name an act the command would not take, because the command re-derives
    it from the same subject at the moment it runs.

    Every message stands on its own (there are no replies), so the subject is enough to say
    what one is for. The rules, decided against the constants the *filing* commands match on:

    - a **key issued to you** is `save`: the thing to do with a key is take it;
    - somebody else's **key request**, seen by staff, is `authorize` — the grant they are
      waiting for. Not your own: what you await on that one is the reply, not a self-grant;
    - a **pull request**, seen by staff, is `merge`. No `is_own` exclusion here, unlike a key
      request: the owner pushes and merges their own branch as a matter of course;
    - everything else is `read`, which is also what a rung below staff gets on the two staff
      acts. That is the honest answer rather than a refusal — a reader offered a grant they
      can never make is worse off than one shown prose.

    Args:
        subject: The message's subject line, as the spool stored it.
        is_staff: Whether the caller is at :data:`~solver.web.msg.identity.STAFF_FLOOR`.
        is_own: Whether the caller wrote this message.
    """
    if subject.startswith(KEY_ISSUE_SUBJECT):
        return 'save'
    if subject.startswith(KEY_REQUEST_SUBJECT) and is_staff and not is_own:
        return 'authorize'
    if subject.startswith(PR_REVIEW_SUBJECT) and is_staff:
        return 'merge'
    return 'read'


#: Env var naming the public spool socket (the per-user service and the shell read it).
MSG_SOCKET_ENV: str = 'EULER_MSG_SOCKET'
#: Env var naming the local admin socket (the staff terminal path reads it).
ADMIN_SOCKET_ENV: str = 'EULER_MSG_ADMIN_SOCKET'
#: Production socket paths, overridable via the env vars above. The public socket joins
#: the shared `/run/euler` fabric (`euler-web`-only, which the operator's own uid
#: deliberately is not). The admin socket sits in this service's **own** runtime dir —
#: `/run/euler-msg`, systemd's `RuntimeDirectory=` at `0700 euler-msg` — rather
#: than in `/run/euler-adm`, which is euler-auth-private (`0750 euler-auth`) and
#: therefore not writable by this service. Each admin plane owning its own directory is
#: also the better shape: root traverses either, and nothing else traverses both.
DEFAULT_MSG_SOCKET: str = '/run/euler/msg.sock'
DEFAULT_ADMIN_SOCKET: str = '/run/euler-msg/admin.sock'

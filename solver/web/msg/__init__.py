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

__all__ = ['KEY_ISSUE_SUBJECT',
           'KEY_REQUEST_SUBJECT', 'KEY_SHARE_SUBJECT', 'PR_REVIEW_SUBJECT',
           'UNREGISTERED_SUBJECT', 'verb_for']

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

#: The subject **half** a master key is delivered under — `key-split`'s message. The other
#: half is the share committed in the repository, so acting on this one is `key-reconstruct`
#: rather than a plain write. Like an issued key the payload is sealed to the recipient's
#: public key, and unlike one it is inert even opened: without a current clone it is half a
#: key. Named here with the other two for the same reason — three parties have to
#: agree on it (`key-split` files it, :func:`verb_for` reads it, `msg act` re-checks it before
#: it will put two halves of a key together).
KEY_SHARE_SUBJECT: str = 'Master key share for '

#: The subject a pull request is announced under — `git-push` files it the moment it opens
#: one, and :func:`verb_for` reads it to make `msg act` on such a message the merge itself.
#: A wire convention like the two above, and for the same reason: the chip must never name
#: an act the command would not take. Unlike a key message the body is not a payload — the
#: review happens against GitHub's queue, not the spool — so this is a pure nudge, and the
#: **branch in the subject is the correlation**, in both directions: acting on the message
#: resolves it into the request to merge (`solver.core.git.merge_pr_for_branch`), and the
#: merge dismisses the notice by matching this subject once the branch has landed
#: (`solver.core.git._dismiss_pr_notice`). Which is why the branch is part of the subject
#: rather than only of the body.
PR_REVIEW_SUBJECT: str = 'Pull request ready for review: '

#: The subject `summary` files under when the progress page disagrees with what is recorded
#: as solved: a problem `mark` set solved whose answer projecteuler.net has never been given
#: — so it is solved here and not there. Prose for a person to read (the verb is a plain
#: `msg read`), named here so it sits with the other command-filed subjects rather than
#: being invented at the call site.
UNREGISTERED_SUBJECT: str = 'Answer not registered for '


def verb_for(subject: str, *, is_staff: bool, is_own: bool) -> str:
    """What a message is asking to have done: `save` | `reconstruct` | `authorize` | `merge` | `read`.

    **The one rule, in one place.** `msg act <id>` runs it and the header's message chip
    labels its rows with it (:mod:`solver.web.user.msg_api`), so the two cannot drift — the
    chip can never name an act the command would not take, because the command re-derives
    it from the same subject at the moment it runs.

    Every message stands on its own (there are no replies), so the subject is enough to say
    what one is for. The rules, decided against the constants the *filing* commands match on:

    - a **key issued to you** is `save`: the thing to do with a key is take it;
    - **half a key** is `reconstruct`: the same thing to do, one step longer — it is completed
      with the half your clone already carries before there is a key to take;
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
    # The share subject first: it is not a prefix of the issue one, but the two read alike,
    # and the order says which is which without anybody having to check that.
    if subject.startswith(KEY_SHARE_SUBJECT):
        return 'reconstruct'
    if subject.startswith(KEY_ISSUE_SUBJECT):
        return 'save'
    if subject.startswith(KEY_REQUEST_SUBJECT) and is_staff and not is_own:
        return 'authorize'
    if subject.startswith(PR_REVIEW_SUBJECT) and is_staff:
        return 'merge'
    return 'read'


# The socket paths and the variables that override them are settings, and live in the one
# table: `[msg]` in `solver/config/env.conf`, read through `solver.config.env.load_spec`.
# The reasoning that picks those values belongs beside them and is recorded there — the
# public socket joins the shared `/run/euler` fabric (`euler-web`-only, which the
# operator's own uid deliberately is not), while the admin socket sits in this service's
# **own** runtime dir, `/run/euler-msg`, rather than in euler-auth-private `/run/euler-adm`.

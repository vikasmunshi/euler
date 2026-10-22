#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Notices: what a command tells the people who act on it — through whatever carries it.

Some commands finish by handing work to somebody else: `git-push` opens a pull request a
maintainer lands, `summary` finds answers nobody registered, `user` mints a key that needs
issuing. The solver shell names the notice; it does not deliver it. A front end that has a way
to — the web shell's message spool — installs a :class:`Delivery` through its
:class:`~solver.shell.extension.Extension`. With none installed nothing is sent, and each
caller says what to do by hand instead.

This is the escape hatch docs/package-guide.md § 3.3 keeps for what an overlay cannot express:
the notice's text depends on what the command found half way through.

The **subjects** are the contract between the commands that file notices and the spool that
reads them (its chip offers `merge` on a review row, `save` on a key row), so they live here, on
the side both can import. Stdlib-only.
"""
from __future__ import annotations

__all__ = ['KEY_ISSUE_SUBJECT', 'KEY_REQUEST_SUBJECT', 'KEY_SHARE_SUBJECT', 'PR_REVIEW_SUBJECT',
           'UNREGISTERED_SUBJECT', 'Delivery', 'dismiss', 'install', 'key_hint', 'to_staff']

from typing import Protocol

#: The subject a key-authorization request is filed under — the one message *kind* the
#: spool carries that another command can work. A wire convention between three parties that
#: must not drift: `user` files it (:mod:`solver.crypto.keys`), `user-authorize <id>` requires
#: it before reading a public key out of a body, and the spool's `verb_for` reads it to make
#: `msg act` on such a message *be* that grant. Anything else in the spool is prose for a person to read.
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
#: agree on it (`key-split` files it, the spool's `verb_for` reads it, `msg act` re-checks it before
#: it will put two halves of a key together).
KEY_SHARE_SUBJECT: str = 'Master key share for '

#: The subject a pull request is announced under — `git-push` files it the moment it opens
#: one, and the spool's `verb_for` reads it to make `msg act` on such a message the merge itself.
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


class Delivery(Protocol):
    """How notices travel, supplied by a front end."""

    def to_staff(self, subject: str, body: str) -> bool:
        """File a notice with staff; True if it was delivered."""
        ...

    def dismiss(self, subject: str) -> bool:
        """Drop the staff notices filed under *subject*; True if any went."""
        ...

    def key_hint(self) -> str:
        """Where a waiting master key is taken, in this front end's words."""
        ...


class _Nowhere:
    """No front end: nothing is delivered, and a waiting key arrives by hand."""

    def to_staff(self, subject: str, body: str) -> bool:
        return False

    def dismiss(self, subject: str) -> bool:
        return False

    def key_hint(self) -> str:
        return ('run [accent]host-unlock[/accent] with the block you were sent, or '
                '[accent]key-reconstruct[/accent] with a share.')


_delivery: Delivery = _Nowhere()


def install(delivery: Delivery | None) -> None:
    """Make *delivery* carry this process's notices (None: nothing is delivered)."""
    global _delivery
    _delivery = delivery if delivery is not None else _Nowhere()


def to_staff(subject: str, body: str) -> bool:
    """File a notice with staff; best-effort — True only if it was delivered."""
    return _delivery.to_staff(subject, body)


def dismiss(subject: str) -> bool:
    """Drop the staff notices filed under *subject*; True if any went."""
    return _delivery.dismiss(subject)


def key_hint() -> str:
    """What to do about a master key waiting to be taken."""
    return _delivery.key_hint()

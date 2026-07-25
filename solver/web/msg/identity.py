#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Who is calling: ``SO_PEERCRED`` → login → identity → profile.

The spool authenticates by the **kernel**, not by a header or a token. A connection
on ``msg.sock`` carries the peer's uid, which the per-user unit already calls the
authoritative identity (web-server-guide § The per-user tier), and this module turns
it into the same ``(identity, profile)`` pair every other enforcement point uses:

1. ``SO_PEERCRED`` on the accepted socket → the caller's **uid**;
2. :mod:`pwd` → its **login name**, which for a collaborator *is* their
   :func:`~solver.auth.identity.system_slug`;
3. ``authorizations.json`` → the **identity** behind that name, and its **profile**.

Step 3 needs no help from the auth service, and that is what keeps this service
independent of it: :func:`~solver.auth.identity.system_slug` is a pure SHA-1 of the
normalised e-mail, so recomputing it over every identity in the world-readable policy
file yields the ``slug → e-mail`` map — the same trick ``status-web`` uses to label the
collaborator roster. A bare login name (the operator) is looked up directly.

The policy is re-read whenever the file's mtime moves, so a ``users change`` reaches
this service within one request rather than at some next restart — the immediate-revocation
rule of § Authorization applies here too.

**Boxes.** A message is addressed to a *box key*: a web identity's box is its slug, a
local os-login's box is the login name itself. Both are unique strings in the same
namespace, and using the name the kernel reports means the store never has to hold an
e-mail address to route a message.
"""
from __future__ import annotations

__all__ = ['PolicyView', 'box_of', 'peer_uid']

import os
import pwd
import socket
import struct
from pathlib import Path

from solver.auth.authorizations import AUTHZ_FILE_ENV, DEFAULT_AUTHZ_FILE, Authorizations
from solver.auth.identity import system_slug
from solver.auth.subject import rank

#: The floor at which an identity counts as **staff** — the far end of every
#: user→staff message, and the only rung that may broadcast.
STAFF_FLOOR: str = 'maintainer'

#: ``struct ucred`` — pid, uid, gid — as returned by ``SO_PEERCRED``.
_UCRED = struct.Struct('3i')


def peer_uid(sock: socket.socket) -> int | None:
    """The uid on the far end of *sock*, or None if it cannot be read.

    Unix-socket peer credentials are set by the kernel at ``connect()`` time and
    cannot be forged by the peer — which is why nothing on this wire carries a
    sender field. A non-``AF_UNIX`` transport (a dev TCP run) has none.
    """
    try:
        raw = sock.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, _UCRED.size)
    except (OSError, AttributeError, NameError):
        return None
    _pid, uid, _gid = _UCRED.unpack(raw)
    return int(uid)


def box_of(identity: str) -> str:
    """The box key for *identity*: a web e-mail's slug, or a bare login unchanged.

    The one place the mapping is defined. Everything the store holds is keyed by this,
    so the spool routes by the same name the kernel reports for a connecting uid.
    """
    name = identity.strip().lower()
    return system_slug(name) if '@' in name else name


def _policy_path() -> Path:
    """The policy file this service reads — the same resolution order as the kernel's."""
    return Path(os.environ.get(AUTHZ_FILE_ENV) or DEFAULT_AUTHZ_FILE)


class PolicyView:
    """A cached, box-indexed view of ``authorizations.json``.

    Rebuilt whenever the file's mtime changes (and on the first call), so a profile
    change lands within one request. A missing or unreadable file yields an empty view:
    nobody resolves, every gated verb refuses — fail-closed, the same posture as the
    kernel's own default.
    """

    def __init__(self) -> None:
        self._mtime: float = -1.0
        #: box key → (identity, profile)
        self._by_box: dict[str, tuple[str, str]] = {}

    def _refresh(self) -> None:
        """Re-read the policy if its mtime moved (or it appeared / vanished)."""
        try:
            mtime = _policy_path().stat().st_mtime
        except OSError:
            mtime = 0.0
        if mtime == self._mtime and self._by_box:
            return
        self._mtime = mtime
        self._by_box = {box_of(identity): (identity, profile)
                        for identity, profile in Authorizations.load().all_users().items()}

    def resolve(self, name: str) -> tuple[str, str] | None:
        """``(identity, profile)`` for *name*, or None if the policy maps no such principal.

        *name* may be either form, because :func:`box_of` collapses them: an OS login
        (what :mod:`pwd` reports for a connecting uid — a collaborator's slug, or the
        operator's own login name) or a full web identity (what the admin plane asserts
        on the operator's behalf).
        """
        self._refresh()
        return self._by_box.get(box_of(name))

    def resolve_uid(self, uid: int) -> tuple[str, str, str] | None:
        """``(box, identity, profile)`` for *uid*, or None if it maps to nobody."""
        try:
            login = pwd.getpwuid(uid).pw_name
        except KeyError:
            return None
        found = self.resolve(login)
        return None if found is None else (box_of(found[0]), found[0], found[1])

    def box_for_identity(self, identity: str) -> str | None:
        """The box key for a *named* recipient, or None when the policy maps no such identity.

        A notice may only be addressed to someone the policy knows: an unmapped address
        would create a box nobody can ever read, and silently accepting it would report
        success for a message that can never be delivered.
        """
        self._refresh()
        box = box_of(identity)
        return box if box in self._by_box else None

    def staff_boxes(self) -> list[str]:
        """Every box at or above :data:`STAFF_FLOOR` — the inbound queue's readers."""
        self._refresh()
        floor = rank(STAFF_FLOOR)
        return sorted(box for box, (_identity, profile) in self._by_box.items()
                      if rank(profile) >= floor)

    def all_boxes(self) -> list[str]:
        """Every box the policy maps — the broadcast recipient set."""
        self._refresh()
        return sorted(self._by_box)

    def identity_of(self, box: str) -> str:
        """The identity behind *box*, or the box key itself when it maps to none.

        Used for display only (the staff queue names its senders), so an unmapped box —
        a collaborator removed since they wrote — degrades to its slug rather than
        dropping the message.
        """
        self._refresh()
        found = self._by_box.get(box)
        return found[0] if found is not None else box

    def is_web(self, box: str) -> bool:
        """Whether *box* belongs to a web identity — i.e. has a per-user instance to push to."""
        self._refresh()
        found = self._by_box.get(box)
        return found is not None and '@' in found[0]

#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The authorization **subject** — the resolved security principal.

One immutable value describing *who* is running this process and *what* they may
do, resolved once at startup by :func:`solver.auth.identity.resolve_subject`.
Every enforcement point (the command decorator, the web app router) checks
against it; nothing else re-derives identity.

Authorization is a **plain profile ladder** (the multi-tenant re-simplification):
a command or route declares the *minimum profile* it needs, and the check is a
rank comparison on :data:`LADDER`. The earlier ``object:permission`` grant sets
existed to drive per-path filesystem ACLs on the shared operator tree — the
per-user model (every collaborator in their own clone, as their own uid) made
that whole layer redundant.
"""
from __future__ import annotations

__all__ = ['LADDER', 'Subject', 'rank']

from typing import NamedTuple

#: The profile ladder, weakest → strongest. Structural, not configuration: code,
#: templates, and the provisioning kits all branch on these names, so the order
#: lives here in code; ``authorizations.json`` carries only the users map (its
#: optional ``ladder`` field is validated against this).
LADDER: tuple[str, ...] = ('reader', 'contributor', 'maintainer', 'admin')

_RANK: dict[str, int] = {name: index for index, name in enumerate(LADDER)}


def rank(profile: str) -> int:
    """The ladder rank of *profile* (0 = ``reader`` … 3 = ``admin``); ``-1`` if unknown."""
    return _RANK.get(profile, -1)


class Subject(NamedTuple):
    """The resolved principal: identity, channel, and profile.

    - ``user``        — the raw identity (email for web, OS login for terminal),
                        for prompts/logs and per-user state.
    - ``slug``        — filesystem-safe form of ``user`` (per-user state dirs).
    - ``channel``     — ``'terminal'`` or ``'web'``: where this process runs.
    - ``auth_method`` — how identity was proven (``shell-ticket`` / ``os-login``
                        / ``checkout-owner``), for audit.
    - ``profile``     — the assigned rung (``reader``/``contributor``/
                        ``maintainer``/``admin``).
    """

    user: str
    slug: str
    channel: str
    auth_method: str
    profile: str

    def has(self, floor: str) -> bool:
        """True if this subject's profile is at or above *floor* on the ladder.

        Fail-closed twice over: an unknown *floor* is satisfied by no one, and an
        unknown profile satisfies nothing.
        """
        need: int = rank(floor)
        held: int = rank(self.profile)
        return need >= 0 and held >= need

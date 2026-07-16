#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The authorization policy — ``authorizations.json`` (DD-12, re-simplified).

Authorization is a **plain profile ladder** (:data:`solver.auth.subject.LADDER`):
a command or route declares its minimum profile, and enforcement is a rank
comparison. The policy file therefore carries exactly one decision — *who has
which profile*:

- ``users`` — identity → profile, keyed by **web email _or_ OS-login name**
  (one map for both channels); :meth:`profile_for` looks it up (normalised).
- ``ladder`` — optional; documents the rung order and is validated against the
  in-code :data:`~solver.auth.subject.LADDER` (a mismatch fails loudly rather
  than silently reordering trust).

The earlier ``profiles``/``grants``/``objects`` sections existed to drive
per-path filesystem ACLs on the shared operator tree; the per-user model (each
collaborator in their own clone as their own uid) retired that layer, so the
grant vocabulary went with it. A legacy-shaped file still loads — its ``users``
map is all that is read.

**System of record** is ``/etc/euler/authorizations.json`` (root-owned, outside
the repo; mutated only through the sudo-gated ``users`` path). This module reads
it — or the ``EULER_AUTHZ_FILE`` override — and falls back to :data:`_DEFAULT_POLICY`
(an empty users map) so a fresh checkout works before the file is deployed: the
checkout owner floors to ``admin`` by uid, and real deployments seed the map at
install. The default is a literal rather than a shipped file because it carries no
information — the ladder is code (:data:`~solver.auth.subject.LADDER`) and the map
starts empty.

Stdlib-only and free of any ``solver.config`` dependency: :mod:`solver.config`
imports the resolver during its own construction.
"""
from __future__ import annotations

__all__ = ['Authorizations', 'AUTHZ_FILE_ENV', 'DEFAULT_AUTHZ_FILE']

import json
import os
from pathlib import Path
from typing import Any

from solver.auth.subject import LADDER

#: Environment override for the policy file location (tests / dev / services).
AUTHZ_FILE_ENV: str = 'EULER_AUTHZ_FILE'
#: The deployed system-of-record location.
DEFAULT_AUTHZ_FILE: str = '/etc/euler/authorizations.json'
#: The built-in default: nobody is mapped, so only the checkout-owner uid floor applies.
_DEFAULT_POLICY: dict[str, Any] = {'users': {}}


def _normalise(identity: str) -> str:
    """The lookup key for the ``users`` map (trim + lowercase — matches web email keys)."""
    return identity.strip().lower()


class Authorizations:
    """A loaded, queried view of ``authorizations.json`` (immutable once built)."""

    def __init__(self, policy: dict[str, Any]) -> None:
        ladder = policy.get('ladder')
        if ladder is not None and tuple(str(p) for p in ladder) != LADDER:
            raise ValueError(f'authorizations.json ladder {ladder!r} does not match the '
                             f'code ladder {list(LADDER)!r} — the rung order is structural')
        self._users: dict[str, str] = {_normalise(k): str(v) for k, v in (policy.get('users') or {}).items()}

    # ── loading ────────────────────────────────────────────────────────────────────

    @classmethod
    def load(cls) -> Authorizations:
        """Load the policy from the first of: ``$EULER_AUTHZ_FILE``, the deployed SoR,
        else the built-in default (an empty users map).
        """
        for candidate in (os.environ.get(AUTHZ_FILE_ENV), DEFAULT_AUTHZ_FILE):
            if not candidate:
                continue
            try:
                data = json.loads(Path(candidate).read_text(encoding='utf-8'))
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(data, dict):
                return cls(data)
        return cls(dict(_DEFAULT_POLICY))

    # ── queries ────────────────────────────────────────────────────────────────────

    def known_profiles(self) -> frozenset[str]:
        """The set of valid profile names (the code ladder)."""
        return frozenset(LADDER)

    def profile_for(self, identity: str) -> str | None:
        """The profile assigned to *identity* in the ``users`` map, or None if unlisted."""
        return self._users.get(_normalise(identity))

    def all_users(self) -> dict[str, str]:
        """The whole ``users`` map (identity → profile) — web emails and OS logins alike."""
        return dict(self._users)

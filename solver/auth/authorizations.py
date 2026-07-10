#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The authorization policy — ``authorizations.json`` (DD-12).

The single RBAC policy shared by the shell and the web. Three sections:

- ``profiles`` — each a set of ``object:permission`` ``grants`` plus a
  single-parent ``inherits`` (so grants stay DRY); :meth:`permissions_for`
  expands the chain.
- ``users`` — identity → profile, keyed by **web email _or_ OS-login name**
  (one map for both channels); :meth:`profile_for` looks it up (normalised).
- ``objects`` — the permission namespace → filesystem paths; the path-bearing
  ones drive the OS-ACL layer, the path-less ones are pure capabilities.

**System of record** is ``/etc/euler/authorizations.json`` (root-owned, outside
the repo; mutated only through the sudo-gated ``users`` path). This module reads
it — or the ``EULER_AUTHZ_FILE`` override — and falls back to a built-in default
(the DD-12 ladder) so a fresh checkout works before the file is deployed.

Stdlib-only and free of any ``solver.config`` dependency: :mod:`solver.config`
imports the resolver during its own construction.
"""
from __future__ import annotations

__all__ = ['Authorizations', 'AUTHZ_FILE_ENV', 'DEFAULT_AUTHZ_FILE']

import json
import os
from pathlib import Path
from typing import Any

#: Environment override for the policy file location (tests / dev / services).
AUTHZ_FILE_ENV: str = 'EULER_AUTHZ_FILE'
#: The deployed system-of-record location (DD-12).
DEFAULT_AUTHZ_FILE: str = '/etc/euler/authorizations.json'

#: Permission a command/route falls back to when it declares no ``requires`` —
#: fail-closed to admin-only, so a new command is never silently exposed.
FAILCLOSED_PERMISSION: str = 'infra:execute'

#: Built-in default policy (the DD-12 ladder), used when no file is deployed. The
#: ``users`` map is intentionally empty here — the checkout owner floors to
#: ``admin`` by uid, and real deployments seed the map at install.
_DEFAULT_POLICY: dict[str, Any] = {
    'profiles': {
        'reader': {'inherits': None,
                   'grants': ['solver:execute', 'solutions:read', 'docs:read',
                              'web-content:read', 'users:read']},
        'contributor': {'inherits': 'reader',
                        'grants': ['solutions:write', 'solutions:execute']},
        'maintainer': {'inherits': 'contributor',
                       'grants': ['solutions:delete', 'ai:execute']},
        'admin': {'inherits': 'maintainer',
                  'grants': ['shell:execute', 'infra:execute', 'users:write']},
    },
    'users': {},
    'objects': {
        'solutions': ['solutions/'], 'docs': ['docs/'], 'web-content': ['web-content/'],
        'solver': [], 'shell': ['/bin/bash'], 'ai': [], 'users': [], 'infra': [],
    },
}


def _normalise(identity: str) -> str:
    """The lookup key for the ``users`` map (trim + lowercase — matches web email keys)."""
    return identity.strip().lower()


class Authorizations:
    """A loaded, queried view of ``authorizations.json`` (immutable once built)."""

    def __init__(self, policy: dict[str, Any]) -> None:
        self._profiles: dict[str, dict[str, Any]] = policy.get('profiles') or {}
        self._users: dict[str, str] = {_normalise(k): str(v) for k, v in (policy.get('users') or {}).items()}
        self._objects: dict[str, list[str]] = {k: list(v) for k, v in (policy.get('objects') or {}).items()}
        self._perm_cache: dict[str, frozenset[str]] = {}

    # ── loading ────────────────────────────────────────────────────────────────────

    @classmethod
    def load(cls, *, repo_fallback: Path | None = None) -> Authorizations:
        """Load the policy from the first of: ``$EULER_AUTHZ_FILE``, the deployed SoR,
        an optional repo fallback, else the built-in default.
        """
        for candidate in (os.environ.get(AUTHZ_FILE_ENV), DEFAULT_AUTHZ_FILE,
                          str(repo_fallback) if repo_fallback else None):
            if not candidate:
                continue
            try:
                data = json.loads(Path(candidate).read_text(encoding='utf-8'))
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(data, dict):
                return cls(data)
        return cls(_DEFAULT_POLICY)

    # ── queries ────────────────────────────────────────────────────────────────────

    def known_profiles(self) -> frozenset[str]:
        """The set of defined profile names."""
        return frozenset(self._profiles)

    def profile_for(self, identity: str) -> str | None:
        """The profile assigned to *identity* in the ``users`` map, or None if unlisted."""
        return self._users.get(_normalise(identity))

    def all_users(self) -> dict[str, str]:
        """The whole ``users`` map (identity → profile) — web emails and OS logins alike."""
        return dict(self._users)

    def permissions_for(self, profile: str) -> frozenset[str]:
        """The full ``object:permission`` set for *profile*, expanding ``inherits``.

        An unknown profile yields the empty set (fail-closed). Inheritance cycles
        are broken defensively.
        """
        if profile in self._perm_cache:
            return self._perm_cache[profile]
        perms: set[str] = set()
        seen: set[str] = set()
        current: str | None = profile
        while current and current in self._profiles and current not in seen:
            seen.add(current)
            entry = self._profiles[current]
            perms.update(str(g) for g in (entry.get('grants') or []))
            parent = entry.get('inherits')
            current = str(parent) if parent else None
        result = frozenset(perms)
        self._perm_cache[profile] = result
        return result

    def paths_for(self, object_name: str) -> list[str]:
        """The filesystem paths mapped to *object_name* (for the OS-ACL layer); [] if none."""
        return list(self._objects.get(object_name, []))

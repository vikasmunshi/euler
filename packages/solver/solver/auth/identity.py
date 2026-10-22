#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Identity resolution → a :class:`~solver.auth.subject.Subject`.

The solver shell's identity is the **OS login** of the process uid, and its role comes from
a policy the user cannot rewrite (docs/package-guide.md § 2.2):

1. **Who** — the account name of the real uid (`pwd`, never `$USER` / `$LOGNAME`, which the
   user sets).
2. **Role** — when a *root-owned* `authorizations.json` is deployed (`/etc/euler`, or the
   `EULER_AUTHZ_FILE` override if it too is root-owned all the way up), it decides:
   - the login's own entry, if listed;
   - else the e-mail whose :func:`system_slug` *is* this login — a per-user web account,
     so a `solver` run under that uid (claude-solve's headless Claude, a nested
     `solver "…"`) holds its owner's rung, and the entry's e-mail is its identity;
   - else the weakest rung — fail closed low.

   With no policy deployed (a collaborator's own machine) the **checkout owner is `admin`**
   and any other login is `contributor`.

A tamper-proof policy must sit under root-owned directories: a root-owned file in a
user-owned directory can be renamed away and replaced (§ 2.1). The role is a guardrail
inside one uid, not a boundary — the uid, file permissions and the separate-uid services are.

Other front ends (the web shell's one-time ticket) supply their own identity through the
shell's :class:`~solver.shell.extension.Extension`; this module knows nothing of them.

Stdlib-only and free of any `solver.config` dependency (config imports this during
construction).
"""
from __future__ import annotations

__all__ = ['resolve_subject', 'subject_for', 'deployed_policy', 'os_login', 'slugify', 'system_slug']

import hashlib
import os
import pwd
import re
import stat
from pathlib import Path

from solver.auth.authorizations import AUTHZ_FILE_ENV, DEFAULT_AUTHZ_FILE, Authorizations
from solver.auth.subject import LADDER, Subject

_SLUG_KEEP = re.compile(r'[^a-z0-9._-]+')
#: Hex digits of the identity digest that *are* the system slug. The whole name is
#: `u` + this (`ue0f4a1`): a uid, a home directory, a socket name and a git branch,
#: so it is kept short and carries no e-mail local-part. 24 bits is ample separation for
#: a collaborator roster, and provisioning refuses to adopt a pre-existing account name,
#: so a hypothetical collision fails loudly rather than merging two people onto one uid.
_SYSTEM_SLUG_HEX: int = 6


def slugify(identity: str) -> str:
    """Return a filesystem-safe directory name for *identity* (per-user state dirs).

    Lower-cases, collapses any run of characters outside `[a-z0-9._-]` to a
    single `_`, and appends a short hash of the raw identity so two distinct
    identities can never collide onto the same slug (e.g. `a@x`/`a_x`). Used
    for terminal identities; the web/system identity uses :func:`system_slug`.
    """
    base = _SLUG_KEEP.sub('_', identity.strip().lower()).strip('_.')
    digest = hashlib.sha1(identity.encode('utf-8')).hexdigest()[:6]
    return f'{base}-{digest}'


def system_slug(identity: str) -> str:
    """Return a **system-account** slug for *identity* — the per-user uid/home/socket name.

    Stricter and shorter than :func:`slugify`: `u` + a :data:`_SYSTEM_SLUG_HEX`-digit hash of
    the normalised identity (e.g. `ue0f4a1`), matching `^[a-z][a-z0-9]*$` so `useradd`'s
    `NAME_REGEX` accepts it bare — the uid *is* the slug, with no prefix and no home-grown
    length problem. The e-mail local-part is deliberately absent: this name shows up in
    `/home`, in the process table, and in a git branch, none of which need to publish who a
    collaborator is. The e-mail remains the login identity; this is only its derived system name.
    """
    digest = hashlib.sha1(identity.strip().lower().encode('utf-8')).hexdigest()
    return f'u{digest[:_SYSTEM_SLUG_HEX]}'


def os_login() -> str:
    """The account name of this process's real uid — from the password database, not the env."""
    try:
        return pwd.getpwuid(os.getuid()).pw_name
    except KeyError:
        raise SystemExit(f'identity: uid {os.getuid()} has no account name') from None


def _root_owned(path: Path) -> bool:
    """True if *path* and every directory above it are root-owned and writable by root alone."""
    try:
        for part in (path, *path.parents):
            st = part.stat()
            if st.st_uid != 0 or st.st_mode & (stat.S_IWGRP | stat.S_IWOTH):
                return False
    except OSError:
        return False
    return True


def deployed_policy() -> Authorizations | None:
    """The root-owned policy, or None when none is deployed (or the one found is not root's)."""
    for candidate in (os.environ.get(AUTHZ_FILE_ENV), DEFAULT_AUTHZ_FILE):
        if not candidate:
            continue
        path = Path(candidate).absolute()
        if not _root_owned(path):
            continue
        policy = Authorizations.read(path)
        if policy is not None:
            return policy
    return None


def _owns_checkout(root_dir: Path) -> bool:
    """True if the current process uid owns the repo checkout (the local trust anchor)."""
    try:
        return os.getuid() == root_dir.stat().st_uid
    except OSError:
        return False


def subject_for(login: str, *, owner: bool, policy: Authorizations | None) -> Subject:
    """The :class:`Subject` for OS *login*; *owner* = it owns the checkout; *policy* = the
    deployed root-owned policy, or None (see the module docstring for the chain)."""
    if policy is None:
        return Subject(user=login, slug=slugify(login), channel='terminal',
                       auth_method='checkout-owner' if owner else 'os-login',
                       profile='admin' if owner else 'contributor')
    listed = policy.profile_for(login)
    if listed is not None:
        return Subject(user=login, slug=slugify(login), channel='terminal', auth_method='policy', profile=listed)
    for identity, profile in policy.all_users().items():
        if '@' in identity and system_slug(identity) == login:
            return Subject(user=identity, slug=login, channel='terminal', auth_method='policy-account',
                           profile=profile)
    return Subject(user=login, slug=slugify(login), channel='terminal', auth_method='os-login', profile=LADDER[0])


def resolve_subject(root_dir: Path) -> Subject:
    """Resolve the current :class:`Subject` from the OS login and the deployed policy."""
    return subject_for(os_login(), owner=_owns_checkout(root_dir), policy=deployed_policy())

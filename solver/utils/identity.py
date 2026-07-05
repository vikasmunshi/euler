#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Ambient user identity **and profile**: who is this shell running as.

Resolution yields ``(display, slug, profile)``, resolved **once** at startup, in
this precedence order:

1. ``SOLVER_USER`` in the process environment — how ``solver-web`` vouches for
   an already-authenticated web user when it forks a PTY-backed shell (the web
   tier ran the SRP handshake; the child trusts its parent). A terminal user
   may also ``export SOLVER_USER=…`` to pick an identity explicitly.
2. The contents of ``keys/.user-email`` — a machine-local dotfile.
3. ``SOLVER_USER`` in the project ``.env`` file — a project-level default.
4. :func:`getpass.getuser` — the OS login name (the unconfigured local operator).

``display`` keys per-user shell state (history, last problem) via ``slug``;
``profile`` (``admin`` / ``user`` / ``guest``) drives **command authorization**
(see :mod:`solver.shell.command`). The two trust anchors are:

- **Web** — an explicit identity (env / ``.user-email`` / ``.env``) *must* be a
  real, enabled account in ``keys/.users.json``; its stored ``profile`` is used.
  An unknown or disabled identity aborts startup. This is where a web user's
  profile comes from (the parent vouches for the SRP-authenticated email).
- **Local terminal** — with *nothing* configured we fall through to
  :func:`getpass.getuser` and grant the **admin** profile: physical/login access
  to the checkout is the trust (the channel-based half of the model). A local
  operator may still ``export SOLVER_USER=…`` to *drop* to a named account's
  lower profile, but cannot thereby gain anything they don't already have.

Confidentiality proper (web login, solution encryption) is still enforced
elsewhere — SRP in :mod:`solver.web.auth` and the git-filter master key in
:mod:`solver.crypto`; this module only resolves the *profile* those tiers assign.

It lives under :mod:`solver.utils` (an empty-``__init__`` package) rather than
``solver.shell`` so :mod:`solver.config` can import it during construction
without triggering the shell package's own import of ``solver.config``.

The module depends only on the standard library (it is imported while
:mod:`solver.config` is still being constructed, so it must not import back into
``solver``), and deliberately does **not** use ``python-dotenv`` — that is an
optional (``ai`` extra) dependency, absent from a base install.
"""
from __future__ import annotations

__all__ = ['resolve_identity', 'slugify']

import getpass
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

#: Environment variable / ``.env`` key naming the current user.
ENV_VAR: str = 'SOLVER_USER'
#: Machine-local dotfile holding the current user's identity (one line).
USER_EMAIL_FILE: str = 'keys/.user-email'
#: Profile granted to the unconfigured local operator (physical/login access = trust).
LOCAL_PROFILE: str = 'admin'

#: Characters kept verbatim in a slug; everything else becomes ``_``.
_SLUG_KEEP = re.compile(r'[^a-z0-9._-]+')


def _read_env_user(root_dir: Path) -> str | None:
    """Return ``SOLVER_USER`` from the project ``.env`` file, or None.

    A minimal single-key reader (``KEY=VALUE`` lines, ``#`` comments, optional
    surrounding quotes) so identity resolution carries no dependency on
    ``python-dotenv``. A missing or unreadable file yields None.
    """
    env_file = root_dir / '.env'
    try:
        lines = env_file.read_text(encoding='utf-8').splitlines()
    except OSError:
        return None
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, _, value = line.partition('=')
        if key.strip() != ENV_VAR:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        return value or None
    return None


def _read_user_file(root_dir: Path) -> str | None:
    """Return the identity recorded in ``keys/.user-email``, or None if absent/empty."""
    try:
        value = (root_dir / USER_EMAIL_FILE).read_text(encoding='utf-8').strip()
    except OSError:
        return None
    return value or None


def slugify(identity: str) -> str:
    """Return a filesystem-safe directory name for *identity*.

    Lower-cases, collapses any run of characters outside ``[a-z0-9._-]`` to a
    single ``_``, and appends a short hash of the raw identity so two distinct
    identities can never collide onto the same slug (e.g. ``a@x``/``a_x``).
    """
    base = _SLUG_KEEP.sub('_', identity.strip().lower()).strip('_.')
    digest = hashlib.sha1(identity.encode('utf-8')).hexdigest()[:6]
    return f'{base}-{digest}'


def _load_users(users_file: Path) -> dict[str, Any]:
    """Return the ``users`` map from ``users_file``; an empty map if it is absent/invalid."""
    try:
        data: Any = json.loads(users_file.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return {}
    users = data.get('users') if isinstance(data, dict) else None
    return users if isinstance(users, dict) else {}


def resolve_identity(root_dir: Path, users_file: Path) -> tuple[str, str, str]:
    """Resolve the current user, returning ``(display, slug, profile)``.

    *display* is the raw identity for prompts/logs; *slug* is its filesystem-safe
    form for per-user state directories; *profile* (``admin``/``user``/``guest``)
    drives command authorization. See the module docstring for the precedence
    order and the trust model.

    An **explicitly configured** identity (env / ``.user-email`` / ``.env``) must
    resolve to an enabled account in ``users_file`` — an unknown or disabled one
    raises :class:`SystemExit`. With nothing configured, the local operator is
    resolved via :func:`getpass.getuser` and granted the ``admin`` profile.
    """
    display = (os.environ.get(ENV_VAR) or '').strip() or _read_user_file(root_dir) or _read_env_user(root_dir)
    if display:
        user = _load_users(users_file).get(display.strip().lower())
        if user is None or user.get('disabled', True):
            raise SystemExit(f'invalid user: {display}')
        return display, slugify(display), str(user.get('profile', 'user'))
    try:
        display = getpass.getuser()
    except OSError:
        raise SystemExit('could not get login name') from None
    return display, slugify(display), LOCAL_PROFILE

#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Ambient user identity: who is this shell running as, for per-user state.

The identity is a plain string used to key per-user shell state (command
history, the last active problem). It is resolved **once** at startup, in this
precedence order:

1. ``SOLVER_USER`` in the process environment — how ``solver-web`` vouches for
   an already-authenticated web user when it forks a PTY-backed shell (the web
   tier ran the SRP handshake; the child trusts its parent). A terminal user
   may also ``export SOLVER_USER=…`` to pick an identity explicitly.
2. ``SOLVER_USER`` in the project ``.env`` file — a project-level default.
3. The contents of ``keys/.user-email`` — a machine-local dotfile.
4. :func:`getpass.getuser` — the OS login name; ``'default'`` if even that fails.

This is **personalisation, not a security boundary**: the sources above are all
spoofable by whoever runs the process, so per-user state is a convenience, not
an isolation guarantee. Real confidentiality (web access, solution encryption)
is enforced elsewhere — SRP in :mod:`solver.web.auth` and the git-filter master
key in :mod:`solver.crypto`.

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
import os
import re
from pathlib import Path

#: Environment variable / ``.env`` key naming the current user.
ENV_VAR: str = 'SOLVER_USER'
#: Machine-local dotfile holding the current user's identity (one line).
USER_EMAIL_FILE: str = 'keys/.user-email'
#: Fallback identity when even ``getpass.getuser()`` fails.
DEFAULT_USER: str = 'default'

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


def _os_user() -> str:
    """Return the OS login name, or :data:`DEFAULT_USER` when it cannot be determined."""
    try:
        return getpass.getuser() or DEFAULT_USER
    except Exception:  # noqa: BLE001 — getpass can raise on odd/embedded environments
        return DEFAULT_USER


def slugify(identity: str) -> str:
    """Return a filesystem-safe directory name for *identity*.

    Lower-cases, collapses any run of characters outside ``[a-z0-9._-]`` to a
    single ``_``, and appends a short hash of the raw identity so two distinct
    identities can never collide onto the same slug (e.g. ``a@x``/``a_x``).
    """
    base = _SLUG_KEEP.sub('_', identity.strip().lower()).strip('_.') or DEFAULT_USER
    digest = hashlib.sha1(identity.encode('utf-8')).hexdigest()[:6]
    return f'{base}-{digest}'


def resolve_identity(root_dir: Path) -> tuple[str, str]:
    """Resolve the current user, returning ``(display, slug)``.

    *display* is the raw identity for prompts/logs; *slug* is its
    filesystem-safe form for per-user state directories. See the module
    docstring for the precedence order.
    """
    display = (os.environ.get(ENV_VAR) or '').strip() \
        or _read_env_user(root_dir) \
        or _read_user_file(root_dir) \
        or _os_user()
    return display, slugify(display)

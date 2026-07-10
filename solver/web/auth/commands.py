#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The ``users`` shell command: account administration, split by permission (DD-12).

Two paths behind one command:

- **`users list`** needs only ``users:read`` (a ``reader`` grant). It reads the
  world-readable ``authorizations.json`` roster **directly** — no sudo — and prints
  every identity (web email + local OS login) with its profile. An operator holding
  ``users:write`` (admin) additionally gets the full listing (registration state +
  pending invites) via the sudo admin plane.
- **mutations** (`add` / `change` / `enable` / `disable` / `remove`) need
  ``users:write`` (admin) and re-execute the admin CLI (:mod:`solver.web.auth.admin`)
  under ``sudo`` — which writes the root-owned SoR and reaches the euler-auth admin
  socket. The command is registered for ``users:read``; the write verbs are gated at
  **runtime** against the subject's permissions.

Local-terminal only (`channels=('terminal',)`, DD-6): the admin plane is never routed
through Caddy and a web shell cannot sudo.

`add` is two-path: an ``@``-address mints a web invite (the account record appears when
the invitee registers); a bare os-login is a direct map entry (no invite). Password
reset is self-service (DD-7) — there is deliberately no reset verb.
"""
from __future__ import annotations

__all__ = ['users']

import subprocess
import sys
from typing import Literal

from solver.auth import Authorizations
from solver.config import config
from solver.shell import console, register


def _print_roster() -> int:
    """Non-sudo roster from the world-readable authorizations.json (``users:read``)."""
    users = Authorizations.load().all_users()
    if not users:
        console.print('[muted]no users mapped[/muted]')
        return 0
    for name, profile in sorted(users.items()):
        scope = 'web' if '@' in name else 'local'
        console.print(f'  {name:40} {profile:12} [muted]{scope}[/muted]')
    return 0


def _sudo_admin(action: str, identity: str = '', profile: str = '') -> int:
    """Re-execute the admin CLI under sudo (writes the SoR + reaches euler-auth)."""
    argv = ['sudo', sys.executable, '-m', 'solver.web.auth.admin', action]
    if action != 'list':
        argv += [identity, profile]
    try:
        return subprocess.run(argv, check=False).returncode   # sudo prompt + output go to the terminal
    except (OSError, KeyboardInterrupt) as exc:
        console.print(f'[error]error:[/error] could not run the admin CLI ({exc})')
        return 1


@register(requires=('users:read',), channels=('terminal',),
          help_text='List / administer accounts (list is read-only; changes need admin + sudo).')
def users(action: Literal['list', 'add', 'change', 'enable', 'disable', 'remove'] = 'list',
          identity: str = '', profile: Literal['reader', 'contributor', 'maintainer', 'admin'] = 'reader') -> int:
    """Administer accounts on the authorization map + the auth service (DD-12).

    `list` is read-only (``users:read``) and needs no sudo; every mutating verb needs
    ``users:write`` (admin) and re-executes the admin CLI under ``sudo``.

    Args:
        action:   list (roster), add (map entry — ``@email`` also mints an invite;
                  a bare os-login is local-only), change (reassign a profile),
                  enable / disable (web SRP state), remove (drop the account/entry).
        identity: a web email (``@``) or a local OS login (required except for list).
        profile:  the profile to assign (add / change). ``admin`` is valid only for a
                  local os-login, never a web account.
    """
    if action == 'list':
        # Admins get the full sudo listing (SRP state + pending); everyone else the
        # non-sudo roster from the world-readable map.
        return _sudo_admin('list') if config.subject.has('users:write') else _print_roster()

    if not config.subject.has('users:write'):
        console.print('[error]error:[/error] this action needs the [accent]users:write[/accent] '
                      'permission (admin) — run it from the checkout owner\'s local terminal')
        return 1
    if not identity:
        console.print(f'[error]error:[/error] users {action} requires an email or os-login')
        return 2
    return _sudo_admin(action, identity, profile)

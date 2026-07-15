#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The ``users`` shell command: account administration, split by permission (DD-12).

Two paths behind one command:

- **`users list`** is a ``reader``-floor command. A non-admin sees only
  **their own** entry, read directly from the world-readable ``authorizations.json`` — no
  sudo (the reader floor grants sight of your own account, not the roster; MT-10b, since the channel
  axis that used to keep this off the web is gone). An ``admin``
  gets the **full** listing (every identity + registration state + pending invites) via the
  sudo admin plane.
- **mutations** (`add` / `change` / `enable` / `disable` / `remove`) need
  ``admin`` and re-execute the admin CLI (:mod:`solver.web.auth.admin`)
  under ``sudo`` — which writes the root-owned SoR and reaches the euler-auth admin
  socket. The command registers at the ``reader`` floor; the write verbs are gated at
  **runtime** against the subject's permissions.

No longer channel-gated (MT-10 drops the channel axis): the write verbs' real containment is
that they reach the root-owned SoR and the euler-auth **admin socket** only under ``sudo``, which
a web shell (a per-user, non-privileged uid) cannot obtain — so `list` may run anywhere but a
mutation attempted over the web fails at the socket, not at a channel check.

`add` is two-path: an ``@``-address provisions the collaborator's **own OS instance**
(uid, home, a filter-disabled clone on ``user/<slug>``, the socket — via
:mod:`scripts/setup/user.sh`, MT-7) and then mints a web invite (the account record
appears when the invitee registers); a bare os-login is a direct map entry (no instance,
no invite). ``remove`` reverses both: it drops the account, then deprovisions the
instance. Password reset is self-service (DD-7) — there is deliberately no reset verb.
"""
from __future__ import annotations

__all__ = ['users']

import subprocess
import sys
from pathlib import Path
from typing import Literal

from solver.auth import Authorizations
from solver.auth.identity import system_slug
from solver.config import config
from solver.shell import console, register


def _print_roster(only: str | None = None) -> int:
    """Non-sudo roster from the world-readable authorizations.json (reader floor).

    When *only* is given (a non-admin caller), the listing is **scoped to that identity's own
    entry** — the reader floor grants a member sight of their own account, not the whole roster
    (MT-10b). The full roster is an ``admin`` view.
    """
    users = Authorizations.load().all_users()
    if only is not None:
        key = only.strip().lower()
        users = {k: v for k, v in users.items() if k == key}
    if not users:
        console.print('[muted]no users mapped[/muted]' if only is None else '[muted]no account entry[/muted]')
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


def _provision_kit(action: str, slug: str, *rest: str) -> int:
    """Drive the per-user provisioning kit (``scripts/setup/user.sh``) under sudo (MT-7).

    ``provision``/``deprovision`` create or tear down the collaborator's OS instance —
    uid, home, the filter-disabled clone on ``user/<slug>``, and the socket. Best-effort:
    a host without the kit (a plain dev checkout without the web stack laid down) has
    nothing to provision, so a missing script is a note, not a failure — the account map
    + invite still stand and the instance can be laid down later with ``make install-user``.
    """
    script = Path(config.root_dir) / 'scripts' / 'setup' / 'user.sh'
    if not script.exists():
        console.print(f'[muted]note: {script} not present — skipping OS {action} (run make install-user)[/muted]')
        return 0
    try:
        return subprocess.run(['sudo', 'bash', str(script), action, slug, *rest], check=False).returncode
    except (OSError, KeyboardInterrupt) as exc:
        console.print(f'[error]error:[/error] could not run the provisioning kit ({exc})')
        return 1


@register(requires='reader',
          help_text='List / administer accounts (list is read-only; changes need admin + sudo).')
def users(action: Literal['list', 'add', 'change', 'enable', 'disable', 'remove'] = 'list',
          identity: str = '', profile: Literal['reader', 'contributor', 'maintainer', 'admin'] = 'reader') -> int:
    """Administer accounts on the authorization map + the auth service (DD-12).

    `list` is read-only (every rung) and needs no sudo; every mutating verb needs
    ``admin`` and re-executes the admin CLI under ``sudo``.

    Args:
        action:   list (roster), add (map entry — ``@email`` also mints an invite;
                  a bare os-login is local-only), change (reassign a profile),
                  enable / disable (web SRP state), remove (drop the account/entry).
        identity: a web email (``@``) or a local OS login (required except for list).
        profile:  the profile to assign (add / change). ``admin`` is valid only for a
                  local os-login, never a web account.
    """
    if action == 'list':
        # Admins get the full sudo listing (SRP state + pending); a non-admin sees only their
        # own entry (the reader floor = read your own account, not the roster — MT-10b).
        return _sudo_admin('list') if config.subject.has('admin') else _print_roster(config.subject.user)

    if not config.subject.has('admin'):
        console.print('[error]error:[/error] this action needs the [accent]admin[/accent] '
                      'permission (admin) — run it from the checkout owner\'s local terminal')
        return 1
    if not identity:
        console.print(f'[error]error:[/error] users {action} requires an email or os-login')
        return 2

    # A web account (an @-address) gets its own OS instance (MT-7); a bare os-login is the
    # operator's own terminal identity — an existing uid — so it is a map entry only.
    is_web = '@' in identity
    slug = system_slug(identity) if is_web else ''

    if action == 'add':
        if is_web:
            # Provision the OS instance BEFORE minting the invite, so a failed host never
            # leaves a dangling invite to a box with no shell. Provisioning is idempotent.
            rc = _provision_kit('provision', slug, identity, profile)
            if rc != 0:
                console.print('[error]error:[/error] provisioning failed — no invite minted; '
                              'fix the host and re-run `users add`')
                return rc
        return _sudo_admin('add', identity, profile)

    if action == 'remove':
        # Drop the account (SoR + SRP) first; then tear the OS instance down (prompted).
        rc = _sudo_admin('remove', identity, profile)
        if rc == 0 and is_web:
            _provision_kit('deprovision', slug)        # teardown is advisory — the account is already gone
        return rc

    return _sudo_admin(action, identity, profile)      # change | enable | disable

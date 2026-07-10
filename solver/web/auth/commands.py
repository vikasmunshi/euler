#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The ``users`` shell command: account administration, gated by sudo (DD-6).

The admin plane is **wheel-gated**: the admin socket is ``euler-auth``-private
and the ``X-Admin-Token`` lives only in root-readable ``/etc/euler/auth.env``,
so this command simply re-executes the admin CLI
(:mod:`solver.web.auth.admin`) under ``sudo`` — every admin action passes
sudo's password gate (with its usual timestamp caching) and audit trail. An
ordinary operator process holds no admin capability at all.

Local-terminal only by design (DD-6: the admin plane is never routed through
Caddy, and a web shell's uid cannot sudo): ``modules.csv`` loads this module
for the ``terminal`` channel only.

Admins add / list / enable / disable / remove accounts. There is deliberately
**no reset verb** — password reset is self-service (DD-7), and adding a user
only mints an emailed invite: the account record is created when the invitee
completes registration.
"""
from __future__ import annotations

__all__ = ['users']

import subprocess
import sys
from typing import Literal

from solver.shell import console, register


@register(requires=('users:write',), channels=('terminal',),
          help_text='Manage web accounts via the auth service (sudo-gated admin API).')
def users(action: Literal['list', 'add', 'enable', 'disable', 'remove'] = 'list',
          email: str = '', profile: Literal['reader', 'contributor', 'maintainer'] = 'reader') -> int:
    """Administer web accounts through the auth service's local admin socket.

    Re-executes ``python -m solver.web.auth.admin`` under ``sudo`` (the admin
    socket and token are root-only), so expect a sudo password prompt unless
    the timestamp is cached.

    Args:
        action:  add (mint + email a registration invite), list (accounts and
                 pending invites), enable / disable (account switch; disable also
                 kills live sessions), or remove (delete account and invites).
        email:   The account's email (required for everything except list).
        profile: Authorization profile for a new invite (add only).
    """
    if action != 'list' and '@' not in email:
        console.print(f'[error]error:[/error] users {action} requires an email')
        return 2
    argv = ['sudo', sys.executable, '-m', 'solver.web.auth.admin', action]
    if action != 'list':
        argv += [email, profile]
    try:
        # No capture: sudo's password prompt and the CLI's output go straight
        # to the terminal.
        return subprocess.run(argv, check=False).returncode
    except (OSError, KeyboardInterrupt) as exc:
        console.print(f'[error]error:[/error] could not run the admin CLI ({exc})')
        return 1

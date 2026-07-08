#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The admin-plane CLI: run **under sudo** by the ``users`` shell command (DD-6).

The admin plane is gated by **wheel/sudo**, not a bespoke group: the admin
socket is ``euler-auth``-private (``0600``, in ``/run/euler-adm``) and the
``X-Admin-Token`` lives only in the root-readable ``/etc/euler/auth.env`` — so
an ordinary operator process holds *nothing*. Root (via ``sudo``) traverses the
socket and reads the token; every admin action therefore passes sudo's
password gate and audit trail.

Invocation (see :mod:`solver.web.auth.commands` for the shell wrapper)::

    sudo <venv-python> -m solver.web.auth.admin <list|add|enable|disable|remove> [email] [profile]

Configuration: reads ``EULER_AUTH_ENV`` (default ``/etc/euler/auth.env``) for
``EULER_ADMIN_TOKEN`` / ``EULER_AUTH_ADMIN_SOCKET``; direct environment
variables take precedence (dev runs against scratch sockets).
"""
from __future__ import annotations

__all__ = ['main']

import os
import sys
from pathlib import Path
from typing import Any

from solver.web.auth import ADMIN_SOCKET_ENV, DEFAULT_ADMIN_SOCKET
from solver.web.auth.client import request

_ACTIONS = ('list', 'add', 'enable', 'disable', 'remove')


def _env_file_values(path: Path) -> dict[str, str]:
    """Minimal KEY=VALUE reader for the scoped auth env file."""
    values: dict[str, str] = {}
    try:
        lines = path.read_text(encoding='utf-8').splitlines()
    except OSError:
        return values
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, _, value = line.partition('=')
        values[key.strip()] = value.strip().strip('\'"')
    return values


def _fail(message: str, code: int = 1) -> int:
    print(f'error: {message}', file=sys.stderr)
    return code


def main(argv: list[str]) -> int:
    if not argv or argv[0] not in _ACTIONS:
        print(f'usage: python -m solver.web.auth.admin {{{"|".join(_ACTIONS)}}} [email] [profile]',
              file=sys.stderr)
        return 2
    action = argv[0]
    email = argv[1] if len(argv) > 1 else ''
    profile = argv[2] if len(argv) > 2 else 'user'
    if action != 'list' and '@' not in email:
        return _fail(f'users {action} requires an email', 2)

    env_file = _env_file_values(Path(os.environ.get('EULER_AUTH_ENV', '/etc/euler/auth.env')))
    token = os.environ.get('EULER_ADMIN_TOKEN') or env_file.get('EULER_ADMIN_TOKEN', '')
    socket_path = (os.environ.get(ADMIN_SOCKET_ENV) or env_file.get(ADMIN_SOCKET_ENV)
                   or DEFAULT_ADMIN_SOCKET)
    if not token:
        return _fail('EULER_ADMIN_TOKEN not found (is /etc/euler/auth.env deployed, and are you root?)')

    # `add` waits for the invite mail to clear the relay + Gmail submission,
    # which can take many seconds — give it a generous deadline.
    timeout = 60.0 if action == 'add' else 10.0
    try:
        if action == 'list':
            status, data = request(socket_path, 'GET', '/admin/users',
                                   headers={'X-Admin-Token': token}, timeout=timeout)
        elif action == 'add':
            status, data = request(socket_path, 'POST', '/admin/users',
                                   body={'email': email, 'profile': profile},
                                   headers={'X-Admin-Token': token}, timeout=timeout)
        elif action == 'remove':
            status, data = request(socket_path, 'DELETE', f'/admin/users/{email}',
                                   headers={'X-Admin-Token': token}, timeout=timeout)
        else:
            status, data = request(socket_path, 'POST', f'/admin/users/{email}/{action}',
                                   headers={'X-Admin-Token': token}, timeout=timeout)
    except TimeoutError:
        return _fail(f'timed out after {timeout:.0f}s waiting for the auth service '
                     f'(the action may still have completed — check with `users list`)')
    except OSError as exc:
        return _fail(f'auth service unreachable at {socket_path} ({exc}) — is euler-auth.service running?')

    if action == 'list':
        if status != 200 or not isinstance(data, dict):
            return _fail(f'admin API: {status} {data}')
        _print_listing(data)
        return 0
    if action == 'add' and status == 201 and isinstance(data, dict):
        print(f'invited {data.get("email")} ({data.get("profile")}) — link emailed, valid {data.get("expires")}')
        return 0
    if status == 200:
        print(f'{action}d {email}' if action != 'remove' else f'removed {email}')
        return 0
    return _fail(f'{status} {data}')


def _print_listing(data: dict[str, Any]) -> None:
    for record in data.get('users', []):
        state = 'disabled' if record.get('disabled') else 'enabled'
        print(f'  {record.get("email"):40} {record.get("profile"):6} {state:8}'
              f' since {str(record.get("created", "?"))[:10]}')
    for record in data.get('pending', []):
        print(f'  {record.get("email"):40} {record.get("profile"):6} invited '
              f' {record.get("kind")}/{record.get("state")}, expires in {record.get("expires_in_h")}h')
    if not data.get('users') and not data.get('pending'):
        print('no accounts or pending invites')


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))

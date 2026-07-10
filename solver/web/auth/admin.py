#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The admin-plane CLI: run **under sudo** by the ``users`` shell command (DD-6/DD-12).

The admin plane is gated by **wheel/sudo**, not a bespoke group. Running as root
(via ``sudo``) this CLI does two things the operator's ordinary uid cannot:

- **writes the authorization system of record** — ``/etc/euler/authorizations.json``
  (``root:root 0644``) — for profile assignment (``add`` / ``change`` / the map side
  of ``remove``), the DD-12 write path;
- **reaches the euler-auth admin socket** (``0600``, token in root-readable
  ``/etc/euler/auth.env``) for SRP operations — minting invites, enable / disable /
  remove, session revocation, and the full roster listing.

Identity is a **web email** (``@``) or a **local OS login** (bare). A bare name gets
a direct map entry (no invite, no SRP record — a local login authenticates by being
that OS user); an email additionally mints an emailed invite / drives SRP state.

Invocation (see :mod:`solver.web.auth.commands` for the shell wrapper)::

    sudo <venv-python> -m solver.web.auth.admin <list|add|change|enable|disable|remove> [identity] [profile]
"""
from __future__ import annotations

__all__ = ['main']

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

from solver.web.auth import ADMIN_SOCKET_ENV, DEFAULT_ADMIN_SOCKET
from solver.web.auth.client import request

_ACTIONS = ('list', 'add', 'change', 'enable', 'disable', 'remove')
_WEB_PROFILES = ('reader', 'contributor', 'maintainer')          # admin is local-only (DD-11)
_ALL_PROFILES = _WEB_PROFILES + ('admin',)
_AUTHZ_PATH = os.environ.get('EULER_AUTHZ_FILE', '/etc/euler/authorizations.json')


def _fail(message: str, code: int = 1) -> int:
    print(f'error: {message}', file=sys.stderr)
    return code


# ── authorizations.json (the SoR — root-write) ──────────────────────────────────────

def _authz_save(data: dict[str, Any]) -> None:
    """Write the policy back atomically at 0644 (root-owned, world-readable)."""
    path = Path(_AUTHZ_PATH)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f'.{path.name}.')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            json.dump(data, handle, indent=2, sort_keys=True)
            handle.write('\n')
        os.chmod(tmp, 0o644)
        os.replace(tmp, path)
    except BaseException:
        os.unlink(tmp)
        raise


def _authz_set(identity: str, profile: str) -> None:
    data = json.loads(Path(_AUTHZ_PATH).read_text(encoding='utf-8'))
    data.setdefault('users', {})[identity.strip().lower()] = profile
    _authz_save(data)


def _authz_remove(identity: str) -> bool:
    data = json.loads(Path(_AUTHZ_PATH).read_text(encoding='utf-8'))
    if data.get('users', {}).pop(identity.strip().lower(), None) is None:
        return False
    _authz_save(data)
    return True


# ── euler-auth admin socket (SRP operations) ────────────────────────────────────────

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


def _api(method: str, path: str, *, body: dict[str, Any] | None = None,
         timeout: float = 10.0) -> tuple[int, dict[str, Any] | str]:
    """One call to the euler-auth admin socket (raises SystemExit-style on failure)."""
    env_file = _env_file_values(Path(os.environ.get('EULER_AUTH_ENV', '/etc/euler/auth.env')))
    token = os.environ.get('EULER_ADMIN_TOKEN') or env_file.get('EULER_ADMIN_TOKEN', '')
    socket_path = (os.environ.get(ADMIN_SOCKET_ENV) or env_file.get(ADMIN_SOCKET_ENV)
                   or DEFAULT_ADMIN_SOCKET)
    if not token:
        raise RuntimeError('EULER_ADMIN_TOKEN not found (is /etc/euler/auth.env deployed, and are you root?)')
    return request(socket_path, method, path, body=body, headers={'X-Admin-Token': token}, timeout=timeout)


# ── dispatch ────────────────────────────────────────────────────────────────────────

def main(argv: list[str]) -> int:
    if not argv or argv[0] not in _ACTIONS:
        print(f'usage: python -m solver.web.auth.admin {{{"|".join(_ACTIONS)}}} [identity] [profile]',
              file=sys.stderr)
        return 2
    action = argv[0]
    identity = argv[1] if len(argv) > 1 else ''
    profile = argv[2] if len(argv) > 2 else 'reader'
    is_web = '@' in identity

    if action != 'list' and not identity:
        return _fail(f'users {action} requires an email or os-login')
    if action in ('enable', 'disable') and not is_web:
        return _fail(f'users {action} applies to web accounts only (SRP state)')
    if action in ('add', 'change'):
        allowed = _WEB_PROFILES if is_web else _ALL_PROFILES
        if profile not in allowed:
            return _fail(f'profile for {"a web account" if is_web else "a local login"} '
                         f'must be one of {allowed}')

    try:
        if action == 'list':
            status, data = _api('GET', '/admin/users')
            if status != 200 or not isinstance(data, dict):
                return _fail(f'admin API: {status} {data}')
            _print_listing(data)
            return 0

        if action == 'add':
            _authz_set(identity, profile)                        # SoR write (both paths)
            if not is_web:
                print(f'mapped local login {identity} → {profile}')
                return 0
            status, data = _api('POST', '/admin/users', body={'email': identity, 'profile': profile},
                                timeout=60.0)                    # invite mail can take seconds
            if status == 201 and isinstance(data, dict):
                print(f'invited {identity} ({profile}) — link emailed, valid {data.get("expires")}')
                return 0
            _authz_remove(identity)                              # roll back the map entry on failure
            return _fail(f'invite failed ({status} {data}); map entry reverted')

        if action == 'change':
            _authz_set(identity, profile)
            if is_web:
                _api('POST', f'/admin/users/{identity}/revoke')   # new profile takes effect on re-login
            print(f'changed {identity} → {profile}')
            return 0

        if action == 'remove':
            removed_map = _authz_remove(identity)
            removed_srp = False
            if is_web:
                status, _ = _api('DELETE', f'/admin/users/{identity}')
                removed_srp = status == 200
            if not removed_map and not removed_srp:
                return _fail(f'no such user or invite: {identity}')
            print(f'removed {identity}')
            return 0

        # enable | disable (web SRP state)
        status, data = _api('POST', f'/admin/users/{identity}/{action}')
        if status == 200:
            print(f'{action}d {identity}')
            return 0
        return _fail(f'{status} {data}')
    except TimeoutError:
        return _fail('timed out waiting for the auth service (the action may still have completed — '
                     'check with `users list`)')
    except (OSError, RuntimeError) as exc:
        return _fail(f'auth admin plane error ({exc}) — is euler-auth.service running, and are you root?')


def _print_listing(data: dict[str, Any]) -> None:
    """Render the roster — every identity in authorizations.json (web + local) with its
    profile and registration state — plus in-flight invites (DD-12)."""
    roster = data.get('roster', [])
    for entry in roster:
        print(f'  {entry.get("user"):40} {entry.get("profile"):18} '
              f'{entry.get("scope"):6} {entry.get("state")}')
    for record in data.get('pending', []):
        print(f'  {record.get("email"):40} {record.get("profile"):18} '
              f'web    pending {record.get("kind")}/{record.get("state")}, '
              f'expires in {record.get("expires_in_h")}h')
    if not roster and not data.get('pending'):
        print('no accounts or pending invites')


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))

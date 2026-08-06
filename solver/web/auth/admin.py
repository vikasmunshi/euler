#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The admin-plane CLI: run **under sudo** by the `users` shell command.

The admin plane is gated by **wheel/sudo**, not a bespoke group. Running as root
(via `sudo`) this CLI does two things the operator's ordinary uid cannot:

- **writes the authorization system of record** — `/etc/euler/authorizations.json`
  (`root:root 0644`) — for profile assignment (`add` / `change` / the map side
  of `remove`);
- **reaches the euler-auth admin socket** (`0600`, token in root-readable
  `/etc/euler/auth.env`) for SRP operations — minting invites, enable / disable /
  remove, session revocation, and the full roster listing.

Identity is a **web email** (`@`) or a **local OS login** (bare). A bare name gets
a direct map entry (no invite, no SRP record — a local login authenticates by being
that OS user); an email additionally mints an emailed invite / drives SRP state.

Invocation (see :mod:`solver.web.auth.commands` for the shell wrapper)::

    sudo <venv-python> -m solver.web.auth.admin \
        <list|add|change|enable|disable|remove|requests-json|dismiss> [identity] [profile]

`list` now folds in the invite-request queue (the login page's "Request an
invite" form). `requests-json` dumps that queue as JSON for the interactive
`users process-requests` orchestrator, and `dismiss <email>` drops one — both
reach the same admin socket; the queue itself is a euler-auth-private store, never
the SoR.
"""
from __future__ import annotations

__all__ = ['main']

import grp
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from solver.auth.identity import system_slug
from solver.web.auth import ADMIN_SOCKET_ENV, DEFAULT_ADMIN_SOCKET
from solver.web.auth.client import request
from solver.web.envfile import env_file_values

_ACTIONS = ('list', 'add', 'change', 'enable', 'disable', 'remove',
            'roster-json', 'requests-json', 'dismiss')
_NO_IDENTITY = ('list', 'roster-json', 'requests-json')       # the views take no identity
_WEB_PROFILES = ('reader', 'contributor', 'maintainer')          # admin is local-only
_ALL_PROFILES = _WEB_PROFILES + ('admin',)
_AUTHZ_PATH = os.environ.get('EULER_AUTHZ_FILE', '/etc/euler/authorizations.json')
#: The unix group that may write the roster, and the profiles that belong in it.
_MAINT_GROUP = 'euler-maint'
_MAINT_PROFILES = ('maintainer', 'admin')


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


# ── the roster write-ACL group ──────────────────────────────────────────────────────

def _sync_maint_group(identity: str, profile: str, is_web: bool) -> None:
    """Add or remove *identity*'s unix account from `euler-maint`, tracking the profile.

    That group is the write-ACL on `/etc/euler/roster/` — the roster is read by everyone and
    written by maintainers, and unix has no notion of a profile, so membership is what carries
    the floor down to the filesystem. It is **not** a second copy of the ladder: it grants
    "may write an advisory file" and nothing else, so a stale member can record public keys and
    dates on a host they still have an account on, and that is the whole of it.

    Best-effort, and deliberately: the account act itself has already succeeded by the time
    this runs, and a missing group (a host where the roster kit was never laid down) must not
    turn a successful `users change` into a failure. It reports instead.

    Membership is read at login, so a promoted maintainer's **running** service keeps the old
    groups until it restarts — `users redeploy` is what re-lays them.
    """
    account = system_slug(identity) if is_web else identity
    wanted = profile in _MAINT_PROFILES
    try:
        members = grp.getgrnam(_MAINT_GROUP).gr_mem
    except KeyError:
        print(f'note: group {_MAINT_GROUP} is absent — run the auth kit to lay the roster down',
              file=sys.stderr)
        return
    if wanted == (account in members):
        return
    done = subprocess.run(['gpasswd', '-a' if wanted else '-d', account, _MAINT_GROUP],
                          capture_output=True, text=True)
    if done.returncode != 0:
        print(f'note: could not {"add" if wanted else "remove"} {account} '
              f'{"to" if wanted else "from"} {_MAINT_GROUP}: {done.stderr.strip()}', file=sys.stderr)
        return
    print(f'{"added" if wanted else "removed"} {account} '
          f'{"to" if wanted else "from"} {_MAINT_GROUP} (roster write access)')


# ── euler-auth admin socket (SRP operations) ────────────────────────────────────────

def _api(method: str, path: str, *, body: dict[str, Any] | None = None,
         timeout: float = 10.0) -> tuple[int, dict[str, Any] | str]:
    """One call to the euler-auth admin socket (raises SystemExit-style on failure)."""
    env_file = env_file_values(Path(os.environ.get('EULER_AUTH_ENV', '/etc/euler/auth.env')))
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

    if action not in _NO_IDENTITY and not identity:
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
            status, queue = _api('GET', '/admin/requests')          # the invite-request queue, folded in
            if status != 200 or not isinstance(queue, dict):
                return _fail(f'admin API: {status} {queue}')
            _print_requests(queue)
            return 0

        if action == 'roster-json':
            # The roster as data, for `key-rekey`: every identity on the map with its
            # profile, its per-user slug and its registration state. Machine-readable
            # sibling of `list`, exactly as `requests-json` is for the queue — purge has
            # to *decide* from the roster, not read it off a terminal.
            status, data = _api('GET', '/admin/users')
            if status != 200 or not isinstance(data, dict):
                return _fail(f'admin API: {status} {data}')
            print(json.dumps(data.get('roster', [])))
            return 0

        if action == 'requests-json':
            status, data = _api('GET', '/admin/requests')
            if status != 200 or not isinstance(data, dict):
                return _fail(f'admin API: {status} {data}')
            print(json.dumps(data.get('requests', [])))             # machine-readable, for `users process-requests`
            return 0

        if action == 'dismiss':
            status, data = _api('DELETE', f'/admin/requests/{identity}')
            if status == 200:
                print(f'dismissed request from {identity}')
                return 0
            return _fail(f'{status} {data}')

        if action == 'add':
            _authz_set(identity, profile)                        # SoR write (both paths)
            _sync_maint_group(identity, profile, is_web)
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
            _sync_maint_group(identity, profile, is_web)
            if is_web:
                _api('POST', f'/admin/users/{identity}/revoke')   # new profile takes effect on re-login
            print(f'changed {identity} → {profile}')
            return 0

        if action == 'remove':
            _sync_maint_group(identity, 'reader', is_web)        # drop the roster write-ACL first
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


def _pending_note(record: dict[str, Any]) -> str:
    """The in-flight invite / reset, as a suffix to whatever row it belongs to."""
    return f'pending {record.get("kind")}/{record.get("state")}, expires in {record.get("expires_in_h")}h'


def _print_listing(data: dict[str, Any]) -> None:
    """Render the roster — every identity in authorizations.json (web + local) with its
    profile and registration state — plus in-flight invites.

    One identity is one row: a pending record for an identity already on the roster is
    an *attribute* of that account (mid-registration, or a reset in flight), not a
    second account, so it folds into that row's state column. Only a pending record
    with no roster entry — an invite whose map entry has since gone — stands alone.
    """
    roster = data.get('roster', [])
    pending: dict[str, list[dict[str, Any]]] = {}
    for record in data.get('pending', []):
        pending.setdefault(str(record.get('email')), []).append(record)
    for entry in roster:
        # The unix name (the per-user uid/home/socket) for a web account; a local
        # OS login has no per-user instance, so its column is blank.
        notes = [_pending_note(record) for record in pending.pop(str(entry.get('user')), [])]
        state = ' — '.join([str(entry.get('state')), *notes])
        print(f'  {entry.get("user"):40} {entry.get("slug") or "":10} {entry.get("profile"):18} '
              f'{entry.get("scope"):6} {state}')
    for email, records in pending.items():                       # orphans: no account, no map entry
        for record in records:
            # No account exists — hence no unix name — so the slug column is a placeholder,
            # keeping the fields aligned with the roster rows above.
            print(f'  {email:40} {"—":10} {record.get("profile"):18} '
                  f'web    {_pending_note(record)}')
    if not roster and not data.get('pending'):
        print('no accounts or pending invites')


def _print_requests(data: dict[str, Any]) -> None:
    """Render the invite-request queue — prospective collaborators from the public form.

    Printed as its own section under `users list`; work through it with
    `users process-requests`.
    """
    requests = data.get('requests', [])
    print(f'\ninvite requests ({len(requests)}) — process with `users process-requests`:')
    for record in requests:
        submissions = int(record.get('submissions', 1))
        seen = f'  (×{submissions})' if submissions > 1 else ''
        print(f'  {record.get("email"):40} {(record.get("name") or "")[:28]:28} '
              f'{record.get("created", "")}{seen}')
        for line in str(record.get('remarks') or '').splitlines():
            print(f'        {line}')
    if not requests:
        print('  (none)')


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))

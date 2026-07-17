#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The ``users`` shell command: account administration for the operator.

The whole command is **``admin``-floored** and every verb re-executes the admin CLI
(:mod:`solver.web.auth.admin`) under ``sudo`` — which writes the root-owned SoR and
reaches the euler-auth admin socket. That is the real containment: a web shell (a
per-user, non-privileged uid) cannot obtain ``sudo``, so nothing here runs over the
web regardless of the profile floor. The channel is not an authorization axis.

The verbs:

- **`users list`** — the full roster (every identity + registration state + pending
  invites) **and**, folded in as its own section, the **invite-request queue**:
  prospective collaborators who used the login page's "Request an invite" form.
- **`users process-requests`** — work the queue interactively, one request at a time:
  **accept** (provision the instance + mint the invite, then drop it from the queue),
  **ignore** (leave it queued), or **dismiss** (drop it). A request is only intake data
  — accepting it is the sole path that mints an invite and provisions anything.
- **mutations** (`add` / `change` / `enable` / `disable` / `remove`) — the direct
  account verbs, for identities that did not come through the request queue (a bare
  os-login, or an ad-hoc invite).
- **`users redeploy`** — the host plane rather than an account verb: it drives the
  provisioning kit, never the admin CLI, and touches no account — so, like `list`, it
  takes no identity.

`add` is two-path: an ``@``-address provisions the collaborator's **own OS instance**
(uid, home, a filter-disabled clone on ``user/<slug>``, the socket — via
:mod:`scripts/setup/user.sh`) and then mints a web invite (the account record
appears when the invitee registers); a bare os-login is a direct map entry (no instance,
no invite). ``remove`` reverses both: it drops the account, then deprovisions the
instance. ``redeploy`` re-asserts the shared layer across **every** provisioned
collaborator — notably re-laying their git hooks from this checkout, the only plane that
can (their clone cannot be synced from here: the smudge filter needs a master key that
lives in the user's own vault). Password reset is self-service — there is deliberately no
reset verb.
"""
from __future__ import annotations

__all__ = ['users']

import json
import subprocess
import sys
from pathlib import Path
from typing import Literal

from solver.auth.identity import system_slug
from solver.config import config
from solver.shell import console, register

#: Profiles assignable to a web account (``admin`` is local-os-login-only).
_WEB_PROFILES = ('reader', 'contributor', 'maintainer')


def _sudo_admin(action: str, identity: str = '', profile: str = '') -> int:
    """Re-execute the admin CLI under sudo (writes the SoR + reaches euler-auth)."""
    argv = ['sudo', sys.executable, '-m', 'solver.web.auth.admin', action]
    if action != 'list':                                  # only the roster view takes no args
        argv += [identity, profile]
    try:
        return subprocess.run(argv, check=False).returncode   # sudo prompt + output go to the terminal
    except (OSError, KeyboardInterrupt) as exc:
        console.print(f'[error]error:[/error] could not run the admin CLI ({exc})')
        return 1


def _sudo_admin_capture(action: str) -> tuple[int, str]:
    """Run an admin CLI **read** under sudo, capturing stdout (JSON).

    Only stdout is piped — stderr and the tty stay attached, so the sudo password
    prompt still reaches the terminal while the machine-readable payload is captured.
    """
    argv = ['sudo', sys.executable, '-m', 'solver.web.auth.admin', action]
    try:
        proc = subprocess.run(argv, stdout=subprocess.PIPE, text=True, check=False)
        return proc.returncode, proc.stdout
    except (OSError, KeyboardInterrupt) as exc:
        console.print(f'[error]error:[/error] could not run the admin CLI ({exc})')
        return 1, ''


def _provision_kit(action: str, *args: str) -> int:
    """Drive the per-user provisioning kit (``scripts/setup/user.sh``) under sudo.

    ``provision``/``deprovision`` create or tear down one collaborator's OS instance —
    uid, home, the filter-disabled clone on ``user/<slug>``, and the socket — and take a
    slug; ``redeploy`` sweeps every provisioned user and takes none. Best-effort:
    a host without the kit (a plain dev checkout without the web stack laid down) has
    nothing to provision, so a missing script is a note, not a failure — the account map
    + invite still stand and the instance can be laid down later with ``make deploy-user``.
    """
    script = Path(config.root_dir) / 'scripts' / 'setup' / 'user.sh'
    if not script.exists():
        console.print(f'[muted]note: {script} not present — skipping OS {action} (run make deploy-user)[/muted]')
        return 0
    try:
        return subprocess.run(['sudo', 'bash', str(script), action, *args], check=False).returncode
    except (OSError, KeyboardInterrupt) as exc:
        console.print(f'[error]error:[/error] could not run the provisioning kit ({exc})')
        return 1


def _add_account(identity: str, profile: str) -> int:
    """Add an account: a web ``@``-address provisions its instance then mints an invite;
    a bare os-login is a direct map entry only.

    Provisioning runs BEFORE the invite so a failed host never leaves a dangling invite
    to a box with no shell (provisioning is idempotent). Shared by the ``add`` verb and
    the ``process-requests`` accept path.
    """
    if '@' in identity:
        rc = _provision_kit('provision', system_slug(identity), identity, profile)
        if rc != 0:
            console.print('[error]error:[/error] provisioning failed — no invite minted; '
                          'fix the host and retry')
            return rc
    return _sudo_admin('add', identity, profile)


def _process_requests() -> int:
    """Walk the invite-request queue interactively — accept / ignore / dismiss each.

    Reads the queue as JSON from the admin plane (one sudo call), then per request
    offers: **accept** (prompt a web profile, provision + invite, then drop it),
    **ignore** (leave it queued), **dismiss** (drop it), or **quit**. Later account
    mutations reuse the cached sudo credential, so the operator is prompted once.
    """
    rc, out = _sudo_admin_capture('requests-json')
    if rc != 0:
        return rc
    try:
        queue = json.loads(out or '[]')
    except json.JSONDecodeError:
        console.print('[error]error:[/error] malformed request data from the admin plane')
        return 1
    if not queue:
        console.print('[muted]no pending invite requests[/muted]')
        return 0
    console.print(f'[accent]{len(queue)}[/accent] pending invite request(s) — per request: '
                  '[accent]a[/accent]ccept · [accent]i[/accent]gnore · '
                  '[accent]d[/accent]ismiss · [accent]q[/accent]uit')
    for req in queue:
        email = str(req.get('email', ''))
        if '@' not in email:
            continue
        submissions = int(req.get('submissions', 1))
        seen = f'  (×{submissions})' if submissions > 1 else ''
        console.print()
        console.print(f'  [accent]{email}[/accent]  {req.get("name", "")}{seen}')
        for line in str(req.get('remarks') or '').splitlines():
            console.print(f'    [muted]{line}[/muted]')
        choice = console.input('  [accent]a/i/d/q[/accent] > ').strip().lower()[:1]
        if choice == 'q':
            break
        if choice == 'd':
            _sudo_admin('dismiss', email)
            console.print('  [muted]dismissed[/muted]')
            continue
        if choice != 'a':
            console.print('  [muted]ignored (left queued)[/muted]')
            continue
        prompt = f'  [accent]profile[/accent] ({"/".join(_WEB_PROFILES)}) [reader] > '
        prof = console.input(prompt).strip().lower() or 'reader'
        if prof not in _WEB_PROFILES:
            console.print(f'  [error]not a web profile: {prof} — left queued[/error]')
            continue
        if _add_account(email, prof) == 0:
            _sudo_admin('dismiss', email)              # onboarded → drop it from the queue
            console.print(f'  [success]invited {email} ({prof})[/success]')
        else:
            console.print('  [error]invite failed — left queued[/error]')
    return 0


@register(requires='admin',
          help_text='Administer accounts + invite requests (re-executes the admin CLI under sudo).')
def users(action: Literal['list', 'process-requests', 'add', 'change',
                          'enable', 'disable', 'remove', 'redeploy'] = 'list',
          identity: str = '', profile: Literal['reader', 'contributor', 'maintainer', 'admin'] = 'reader') -> int:
    """Administer accounts on the authorization map + the auth service.

    The whole command is ``admin``-floored and every verb re-executes the admin CLI
    under ``sudo`` (the SoR + admin socket are root-only). There is no reader/maintainer
    tier here — a web shell cannot get sudo, so nothing runs over the web.

    Args:
        action:   list (roster + pending + the invite-request queue), process-requests
                  (walk the queue interactively — accept / ignore / dismiss each),
                  add (map entry — ``@email`` also provisions + mints an invite; a bare
                  os-login is local-only), change (reassign a profile), enable / disable
                  (web SRP state), remove (drop the account/entry), redeploy (re-assert
                  the per-user host layer and re-lay every collaborator's git hooks —
                  takes no identity, and drops live shells).
        identity: a web email (``@``) or a local OS login (required for the account
                  verbs; not for list / process-requests / redeploy).
        profile:  the profile to assign (add / change). ``admin`` is valid only for a
                  local os-login, never a web account.
    """
    if action == 'list':
        return _sudo_admin('list')                     # roster + pending + invite-request queue

    if action == 'process-requests':
        return _process_requests()                     # interactive: accept / ignore / dismiss

    if action == 'redeploy':
        # The host plane, not an account verb — so it takes no identity and writes no SoR.
        # `user.sh redeploy` refreshes /etc/euler/user.env, re-lays EVERY provisioned
        # collaborator's git hooks from this checkout, and stops each running instance so
        # its socket re-activates it against the current venv.
        #
        # Sweeping every user is the point: a hook template only reaches collaborators from
        # here, so this is how a new gate lands for all of them rather than only for whoever
        # is next provisioned. The cost is that it drops live web shells — an attached
        # collaborator's PTY dies with their service, and their next request starts a new one.
        return _provision_kit('redeploy')

    if not identity:
        console.print(f'[error]error:[/error] users {action} requires an email or os-login')
        return 2

    if action == 'add':
        return _add_account(identity, profile)

    if action == 'remove':
        # Drop the account (SoR + SRP) first; then tear the OS instance down (prompted).
        rc = _sudo_admin('remove', identity, profile)
        if rc == 0 and '@' in identity:
            _provision_kit('deprovision', system_slug(identity))   # teardown is advisory — the account is already gone
        return rc

    return _sudo_admin(action, identity, profile)      # change | enable | disable

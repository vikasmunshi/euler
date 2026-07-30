#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The `users` shell command: account administration for the operator.

The whole command is **`admin`-floored** and every account verb re-executes the admin
CLI (:mod:`solver.web.auth.admin`) under `sudo` — which writes the root-owned SoR and
reaches the euler-auth admin socket. That is the real containment: a web shell (a
per-user, non-privileged uid) cannot obtain `sudo`, so nothing here runs over the
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
- **`users set-keys`** — register every collaborator's X25519 **public** key, read from the
  enc-key file each of them already holds. It is the registry `key-rekey` reads: with one
  enc-key file per machine there is no central list of who holds the master key, so a
  rotation needs to be told who to re-issue to. Public material only — losing it costs a
  sweep, never access. `user-authorize` registers as it issues when it can sudo; from a web
  shell it cannot, so this catches up. Idempotent, and takes no identity.
- **`users redeploy`** — the host plane rather than an account verb: it drives the
  provisioning kit, never the admin CLI, and touches no account — so, like `list`, it
  takes no identity.

`add` is two-path: an `@`-address provisions the collaborator's **own OS instance**
(uid, home, a filter-disabled clone on `user/<slug>`, the socket — via
:mod:`scripts/setup/user.sh`) and then mints a web invite (the account record
appears when the invitee registers); a bare os-login is a direct map entry (no instance,
no invite). `remove` reverses both: it drops the account, then deprovisions the
instance. `redeploy` re-asserts the shared layer across **every** provisioned
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
from typing import Any, Literal

from solver.auth.identity import system_slug
from solver.config import config
from rich.text import Text

from solver.shell import console, register
from solver.shell.dialogue import SKIP, Action, Choice, choose, walk

#: Profiles assignable to a web account (`admin` is local-os-login-only).
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
    """Drive the per-user provisioning kit (`scripts/setup/user.sh`) under sudo.

    `provision`/`deprovision` create or tear down one collaborator's OS instance —
    uid, home, the filter-disabled clone on `user/<slug>`, and the socket — and take a
    slug; `redeploy` sweeps every provisioned user and takes none. Best-effort:
    a host without the kit (a plain dev checkout without the web stack laid down) has
    nothing to provision, so a missing script is a note, not a failure — the account map
    + invite still stand and the instance can be laid down later with `make deploy-user`.
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
    """Add an account: a web `@`-address provisions its instance then mints an invite;
    a bare os-login is a direct map entry only.

    Provisioning runs BEFORE the invite so a failed host never leaves a dangling invite
    to a box with no shell (provisioning is idempotent). Shared by the `add` verb and
    the `process-requests` accept path.
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

    def render(req: dict[str, Any]) -> Text:
        submissions = int(req.get('submissions', 1))
        line = Text('  ')
        line.append(str(req.get('email', '')), style='accent')
        line.append(f'  {req.get("name", "")}')
        if submissions > 1:
            line.append(f'  (×{submissions})')
        for remark in str(req.get('remarks') or '').splitlines():
            line.append(f'\n    {remark}', style='muted')
        return line

    def accept(req: dict[str, Any]) -> int | None:
        email = str(req.get('email', ''))
        profile = choose('Which profile?', [Choice(p) for p in _WEB_PROFILES], default='reader')
        if _add_account(email, profile) != 0:
            console.print('  [error]invite failed — left queued[/error]')
            return 1
        _sudo_admin('dismiss', email)                  # onboarded → drop it from the queue
        console.print(f'  [success]invited {email} ({profile})[/success]')
        return 0

    def dismiss(req: dict[str, Any]) -> int | None:
        _sudo_admin('dismiss', str(req.get('email', '')))
        return None

    return walk([req for req in queue if '@' in str(req.get('email', ''))],
                {'a': Action('accept', accept), 'i': Action('ignore', SKIP),
                 'd': Action('dismiss', dismiss)},
                render=render, label='pending invite request').rc


def _roster() -> list[dict[str, str]] | None:
    """The account roster as data (sudo read), or None when the admin plane did not answer."""
    rc, payload = _sudo_admin_capture('roster-json')
    if rc != 0:
        return None
    try:
        rows = json.loads(payload or '[]')
    except json.JSONDecodeError:
        return None
    return [row for row in rows if isinstance(row, dict)]


def registered_public_keys() -> dict[str, str] | None:
    """`{identity: public_key}` for every web account — `''` where none is registered.

    The registry :func:`~solver.crypto.keys.key_rekey` re-issues a rotated master key to.
    Lives on this side because reading it is a sudo call to the auth admin plane, and the
    crypto package holds no opinion about accounts.

    None means the plane did not answer at all — which a rotation must treat as a refusal,
    not as "nobody to tell": re-encrypting the tree and then failing to reach the holders
    would lock out everybody at once.
    """
    roster = _roster()
    if roster is None:
        return None
    return {str(row.get('user', '')): str(row.get('public_key', ''))
            for row in roster if row.get('scope') == 'web'}


def _can_elevate() -> bool:
    """Whether `sudo` could possibly work in this process.

    A web shell's service unit sets `NoNewPrivileges=true`, which makes elevation
    impossible for it and every child — so sudo does not merely fail there, it fails
    *loudly*, printing two lines about container configuration that mean nothing to the
    person reading them. Asking the kernel first turns a confusing diagnostic into a path
    not taken.
    """
    try:
        return 'NoNewPrivs:\t1' not in Path('/proc/self/status').read_text()
    except OSError:
        return True                     # no procfs: let sudo speak for itself


def register_public_key(identity: str, public_key: str) -> bool:
    """Record *public_key* against *identity*; False when the admin plane is out of reach.

    Out of reach is the normal case in a **web shell** — `user-authorize` runs at maintainer,
    which cannot sudo — so this reports rather than raises, and the caller prints the command
    for the operator. The grant itself has already been delivered by then; registration only
    decides whether the next rotation can find them.
    """
    if not _can_elevate():
        return False
    return _sudo_admin('set-key', identity, public_key) == 0


@register(requires='admin')
def users(action: Literal['list', 'process-requests', 'add', 'change', 'enable', 'disable',
                          'remove', 'set-keys', 'redeploy'] = 'list',
          identity: str = '',
          profile: Literal['reader', 'contributor', 'maintainer', 'admin'] = 'reader') -> int:
    """Administer accounts on the authorization map + the auth service.

    The whole command is `admin`-floored and the account verbs re-execute the admin CLI
    under `sudo` (the SoR + admin socket are root-only). There is no reader/maintainer
    tier here — a web shell cannot get sudo, so nothing runs over the web.

    `set-keys` sweeps every collaborator and registers the X25519 **public** key each of
    them already holds — the registry `key-rekey` re-issues a rotated master key to. It
    takes no identity and reads no secret: a holder's enc-key file names their public key,
    and that is all it copies. `user-authorize` registers as it issues when it can reach the
    admin plane; a web shell cannot sudo, so this is the sweep that catches up. Idempotent —
    run it whenever `users list` shows a blank column.

    Args:
        action: What to do — `list` the roster, pending invites and the invite-request
            queue; `process-requests` walks that queue interactively (accept / ignore /
            dismiss each); `add` a map entry (`@email` also provisions the account and mints
            an invite, a bare os-login is local-only); `change` reassigns a profile;
            `enable` / `disable` the web SRP state; `remove` drops the account or entry;
            `set-keys` registers every collaborator's public key for rekey; `redeploy`
            re-asserts the per-user host layer and re-lays every collaborator's git hooks,
            dropping live shells. Defaults to `list`.
        identity: Whose account to act on: a web email (with `@`) or a local OS login.
            Required for the account verbs, unused by `list` / `process-requests` /
            `set-keys` / `redeploy`.
        profile: The profile to assign, for `add` / `change`. `admin` is valid only for a
            local os-login, never a web account.
    """
    if action == 'list':
        return _sudo_admin('list')                     # roster + pending + invite-request queue

    if action == 'process-requests':
        return _process_requests()                     # interactive: accept / ignore / dismiss

    if action == 'set-keys':
        # A sweep, not an account verb: it takes no identity and reads each collaborator's
        # own enc-key file for the public key they already hold.
        return _sudo_admin('set-keys')

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

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
  enc-key file each of them already holds, into the host store **and** the tracked roster
  (`users/users.json`, :mod:`solver.auth.roster`). That file is the registry `key-rekey` and
  `key-split` read: with one enc-key file per machine there is no central list of who holds
  the master key, so a rotation needs to be told who to re-issue to — and it must be readable
  without `sudo`, or the shell that most needs it (a maintainer's, over the web) cannot ask.
  Public material only — losing it costs a sweep, never access. Idempotent, takes no identity.
- **`users redeploy`** — the host plane rather than an account verb: it drives the
  provisioning kit, never the admin CLI, and touches no account — so, like `list`, it
  takes no identity.

**Two files, and only one of them decides anything.** The system of record stays where it
was — `/etc/euler/authorizations.json` (root-owned) for the profile, the euler-auth state dir
for SRP — and every gate still reads it. What the account verbs additionally write is the
**tracked roster**, `users/users.json`: slug-keyed, no e-mail addresses, carrying the public
key, the scope, a profile *mirror* for display, and the dates of the operator's own acts
(`invited`, `provisioned`, `key_issued`, `removed`). It exists so that reading who exists and
what key they hold costs no `sudo`; it decides nothing, because every collaborator can write
their own clone of it. `users list` reports where the two disagree.

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

from solver.auth import roster
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


def _sudo_admin_capture(action: str, *, prompt: bool = True) -> tuple[int, str]:
    """Run an admin CLI **read** under sudo, capturing stdout (JSON).

    Only stdout is piped — stderr and the tty stay attached, so the sudo password prompt still
    reaches the terminal while the machine-readable payload is captured.

    Args:
        action: The admin CLI read to run.
        prompt: Let sudo ask for a password when the credential is not cached. Defaults to
            True. False adds `-n` and swallows the refusal, for a read whose value is a
            convenience — a menu of known accounts — where interrupting the caller with a
            password prompt would cost more than the read is worth.
    """
    argv = ['sudo', *([] if prompt else ['-n']), sys.executable,
            '-m', 'solver.web.auth.admin', action]
    try:
        proc = subprocess.run(argv, stdout=subprocess.PIPE, text=True, check=False,
                              stderr=None if prompt else subprocess.DEVNULL)
        return proc.returncode, proc.stdout
    except (OSError, KeyboardInterrupt) as exc:
        if prompt:
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

    The tracked roster is written **last**, and only once the host has actually taken the
    account: it records what this command did, so recording an invite that was never minted
    would put a fiction into a file everybody reads.
    """
    web = '@' in identity
    if web:
        rc = _provision_kit('provision', system_slug(identity), identity, profile)
        if rc != 0:
            console.print('[error]error:[/error] provisioning failed — no invite minted; '
                          'fix the host and retry')
            return rc
    if (rc := _sudo_admin('add', identity, profile)) != 0:
        return rc
    _record_act(identity, profile, 'web' if web else 'local',
                **({'invited': roster.stamp(), 'provisioned': roster.stamp()} if web else {}))
    return 0


def _record_act(identity: str, profile: str, scope: str, **acts: str) -> None:
    """Write what the operator just did into the tracked roster, and say what to commit.

    Acts, not states: `invited` / `provisioned` / `removed` are dated facts about this
    command's own work, so nothing else can make them stale. `profile` rides along as a
    **mirror** for display and menus — `/etc/euler/authorizations.json` remains the file every
    rank comparison reads, and a collaborator editing their own clone changes what they see
    and never what they may do.

    It does not commit. This is the operator's terminal, mid-onboarding, and a command that
    committed on its own would fold an unrelated working tree into a roster change.
    """
    roster.upsert(identity, profile=profile, scope=scope, **acts)
    console.print(f'[muted]Recorded in [accent]{roster.roster_path().name}[/accent] — '
                  'commit and push it so every clone sees them.[/muted]')


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


def account_identities() -> list[str]:
    """Who a message can be addressed to: the tracked roster's live slugs.

    Read from the checkout, so it costs nothing and works everywhere — a web shell included,
    which the old `sudo -n` read never could. The spool routes by slug (`box_of` leaves a
    non-address unchanged), so these names are usable as recipients exactly as they are, and
    no e-mail address has to be published to build the menu.

    Falls back to the host roster when the file has nothing to say — a checkout from before
    the roster existed, or one that has not synced — because a shorter menu is a worse answer
    than a slower one only when it is empty.
    """
    if slugs := roster.slugs(scope='web'):
        return slugs
    rc, payload = _sudo_admin_capture('roster-json', prompt=False)
    if rc != 0:
        return []
    try:
        rows = json.loads(payload or '[]')
    except json.JSONDecodeError:
        return []
    return sorted(str(row['user']) for row in rows
                  if isinstance(row, dict) and row.get('user') and row.get('scope') == 'web')


def registered_public_keys() -> dict[str, str] | None:
    """`{slug: public_key}` for every collaborator the roster records one for.

    The registry :func:`~solver.crypto.keys.key_rekey` re-issues a rotated master key to, and
    :func:`~solver.crypto.keys.key_split` seals a half to. It is a **tracked file** read, not
    an admin-plane one: that is the point of the roster, since the shell that most needs this
    — a maintainer's web shell — can never obtain `sudo`.

    None means the file could not be read as a roster at all, which a rotation must treat as
    a refusal rather than as "nobody to tell": re-encrypting the tree and then failing to
    reach the holders would lock out everybody at once. An empty dict is a different answer
    — a roster that names nobody — and rekey reports that plainly.
    """
    if not roster.roster_path().exists():
        return None
    return roster.public_keys()


def _sweep_keys_into_roster() -> int:
    """Copy every public key the host now holds into the tracked roster.

    The second half of `set-keys`. The admin sweep reads each collaborator's own enc-key file
    (the only place their public key can be read from) and writes the host store; this brings
    the result into the file every clone can read, which is what `key-rekey` and `key-split`
    actually consult. Public material throughout — losing it costs a sweep, never access.
    """
    rows = _roster()
    if rows is None:
        console.print('[error]error:[/error] keys registered on the host, but the roster could '
                      'not be read back — run [accent]users set-keys[/accent] again')
        return 1
    written = 0
    for row in rows:
        identity, public_key = str(row.get('user', '')), str(row.get('public_key', ''))
        if row.get('scope') != 'web' or not public_key:
            continue
        roster.upsert(identity, public_key=public_key, scope='web')
        written += 1
    console.print(f'[success]{written} public key(s) recorded in '
                  f'[accent]{roster.roster_path().name}[/accent].[/success] '
                  '[muted]Commit and push it.[/muted]')
    return 0


def _report_drift() -> None:
    """Say where the tracked roster and the host's system of record disagree.

    The mirror is advisory, which is exactly why it has to be *checked*: a stale entry is
    harmless until somebody trusts it, and the way nobody trusts it is by being told. Two
    disagreements matter, and both are one-liners to fix:

    - somebody on the host who is not in the file — a menu that cannot offer them, and a
      rotation that will not re-issue to them;
    - somebody in the file the host does not know — a recipient the spool will refuse, which
      is the one thing `msg`'s menu must never offer.

    Silent when the host cannot be read at all (no sudo here): that is not drift, it is a
    plane this shell does not have, and the roster stands on its own.
    """
    rows = _roster()
    if rows is None:
        return
    host = {system_slug(str(row.get('user', ''))) if '@' in str(row.get('user', ''))
            else str(row.get('user', '')): str(row.get('profile', ''))
            for row in rows if row.get('user')}
    tracked = {slug: str((roster.user_entry(slug) or {}).get('profile', ''))
               for slug in roster.slugs()}
    for slug in sorted(set(host) - set(tracked)):
        console.print(f'  [warning]drift[/warning] {slug} is on the host but not in '
                      f'{roster.roster_path().name} — `users set-keys` records them')
    for slug in sorted(set(tracked) - set(host)):
        console.print(f'  [warning]drift[/warning] {slug} is in {roster.roster_path().name} but '
                      'not on the host — a message to them would be refused')
    for slug in sorted(set(host) & set(tracked)):
        if tracked[slug] and host[slug] and tracked[slug] != host[slug]:
            console.print(f'  [warning]drift[/warning] {slug}: roster says {tracked[slug]}, the '
                          f'host says [accent]{host[slug]}[/accent] — the host is what applies')


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
        rc = _sudo_admin('list')                       # roster + pending + invite-request queue
        _report_drift()                                # …then what the tracked roster disagrees on
        return rc

    if action == 'process-requests':
        return _process_requests()                     # interactive: accept / ignore / dismiss

    if action == 'set-keys':
        # A sweep, not an account verb: it takes no identity and reads each collaborator's
        # own enc-key file for the public key they already hold.
        if (rc := _sudo_admin('set-keys')) != 0:
            return rc
        return _sweep_keys_into_roster()

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
        if rc == 0:
            # Marked removed, never deleted: the record says a key was once issued to that
            # public key, and a rotation reads `removed` to know not to re-issue. Dropping the
            # row instead would erase the only note that they ever had access.
            _record_act(identity, profile, 'web' if '@' in identity else 'local',
                        removed=roster.stamp())
        return rc

    rc = _sudo_admin(action, identity, profile)        # change | enable | disable
    if rc == 0 and action == 'change':
        # The mirror follows the SoR that just moved. Only `change` touches a profile:
        # enable/disable are SRP state, which deliberately has no copy here.
        _record_act(identity, profile, 'web' if '@' in identity else 'local')
    return rc

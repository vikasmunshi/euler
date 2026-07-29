#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The ``users`` shell command: account administration for the operator.

The whole command is **``admin``-floored** and every account verb re-executes the admin
CLI (:mod:`solver.web.auth.admin`) under ``sudo`` — which writes the root-owned SoR and
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
- **`users purge`** — the *repo* plane: which entries in `keys/enc-key.json` still belong
  to somebody. It joins the file's `owners` attribution (written by `user-authorize`)
  against the roster and offers the keys whose owner is gone or disabled. Only the roster
  read is sudo; the edit happens in your checkout, as you, and is committed like any other
  change. Your own key is never offered, an unattributed key is only purged by name, and
  what it does **not** do — take back a master key somebody already unwrapped — is printed
  every time, with the `key-rekey` that does.
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
from solver.crypto.ciphers import authorised_keys, key_owners, load_private_key, public_key_hex, read_enc_key_file
from solver.crypto.keys import revoke_keys
from solver.shell import console, register
from solver.utils.shell_utils import confirm

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


#: Where a purge candidate's class is decided (`_classify_keys`). The order is the order
#: rows print in: what you must not touch, then what is safe, then what is on offer.
_KEY_CLASSES = ('self', 'active', 'unattributed', 'stale')


def _own_public_key() -> str:
    """This operator's own public key, or '' when it cannot be read.

    The hard guard on purge: an admin who cannot identify their own entry must not be
    allowed to choose entries to delete, because the one they delete may be theirs — and
    with it their access to every private solution in the tree.
    """
    try:
        return public_key_hex(load_private_key().public_key())
    except (FileNotFoundError, ValueError):
        return ''


def _enc_key_is_clean() -> bool:
    """Whether keys/enc-key.json has no uncommitted local changes.

    Purge classifies from the file as committed. A `user --regen` re-wrap is a *local
    stopgap* — deliberately not attributed, and overwritten by the next `git-sync` — so
    purging against a dirty file would decide from a state that is about to be discarded.
    """
    result = subprocess.run(['git', '--no-optional-locks', 'status', '--porcelain', '--',
                             'keys/enc-key.json'], cwd=config.root_dir,
                            stdout=subprocess.PIPE, text=True, check=False)
    return result.returncode == 0 and not result.stdout.strip()


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


def _classify_keys(roster: list[dict[str, str]], mine: str) -> list[tuple[str, str, str]]:
    """Classify every authorised key as (public_key, class, description).

    The join is slug → identity, computed **here** from each roster identity rather than
    read from the roster's own `slug` column: that column is empty for a local os-login
    (which has no per-user instance), and the operator is usually exactly that — so
    trusting it would classify the operator's own key as belonging to nobody.
    """
    data = read_enc_key_file()
    owners = key_owners(data)
    by_slug = {system_slug(str(row.get('user', ''))): row for row in roster}
    rows: list[tuple[str, str, str]] = []
    for key in authorised_keys(data):
        record = owners.get(key, {})
        slug = record.get('slug', '')
        if key == mine:
            rows.append((key, 'self', 'yours — never purged'))
        elif not slug:
            rows.append((key, 'unattributed', 'no owner recorded — purge by key only'))
        elif (row := by_slug.get(slug)) is None:
            rows.append((key, 'stale', f'{slug}: no such account (removed)'))
        elif row.get('state') == 'disabled':
            rows.append((key, 'stale', f'{row.get("user")}: account disabled'))
        else:
            rows.append((key, 'active', f'{row.get("user")} ({row.get("profile")})'))
    return sorted(rows, key=lambda row: _KEY_CLASSES.index(row[1]))


def _print_keys(rows: list[tuple[str, str, str]]) -> None:
    """Render the classification — the whole file, every time, not only the candidates."""
    styles = {'self': 'accent', 'active': 'success', 'unattributed': 'muted', 'stale': 'warning'}
    for key, klass, note in rows:
        console.print(f'  [{styles[klass]}]{klass:13}[/{styles[klass]}] [muted]{key[:16]}…[/muted]  {note}')


def _purge_after(count: int) -> None:
    """What a purge does *not* do, said at the moment it matters.

    Dropping an entry stops that key unwrapping future copies of the file; it does not
    take the master key back from anyone who already holds it, and every committed blob
    stays decryptable with it. So the follow-through is spelled out rather than implied —
    and deliberately not run for you: `key-rekey` re-encrypts the whole private tree, and
    that is not a thing to have happen as a side effect of a bookkeeping verb.
    """
    console.print(f'[success]purged {count} key(s)[/success] from keys/enc-key.json')
    console.print('[muted]This removes the entry, not the access: whoever held that key still has the '
                  'master key, and every committed blob still decrypts with it. To actually revoke:[/muted]')
    console.print('  [accent]key-rekey[/accent]        [muted]# new master key, re-wrapped to the survivors[/muted]')
    console.print('  [accent]git-publish keys[/accent] [muted]# land it — until this, nothing changed '
                  'for anyone[/muted]')


def _purge(key: str, apply: bool) -> int:
    """Report, or work, the purge candidates in keys/enc-key.json."""
    mine = _own_public_key()
    if not mine:
        console.print('[error]error:[/error] cannot read your own public key (no identity, or a locked '
                      'vault) — refusing to purge, since the entry you drop could be your own')
        return 1
    if apply and not _enc_key_is_clean():
        console.print('[error]error:[/error] keys/enc-key.json has uncommitted changes — commit or '
                      'reset them first, so the purge decides from the file everyone shares')
        return 1
    roster = _roster()
    if roster is None:
        console.print('[error]error:[/error] could not read the account roster (is euler-auth.service '
                      'running, and are you able to sudo?)')
        return 1
    rows = _classify_keys(roster, mine)
    if key:
        wanted = key.strip().lower()
        rows = [row for row in rows if row[0] == wanted]
        if not rows:
            console.print(f'[error]error:[/error] {wanted} is not an authorised key in keys/enc-key.json')
            return 1
        if rows[0][1] == 'self':
            console.print('[error]error:[/error] that is your own key — refusing')
            return 1
    console.print(f'[primary]{len(rows)} authorised key(s)[/primary]')
    _print_keys(rows)
    # An explicit key is the escape hatch for the unattributed ones, which are never
    # offered by the walk: the operator has identified it out of band and says so by
    # naming it, so this asks once and takes them at their word.
    if key:
        if not apply:
            console.print('[muted]add [accent]--apply[/accent] to purge it[/muted]')
            return 0
        if not confirm(f'Purge {rows[0][0]} ({rows[0][2]})?'):
            console.print('[muted]nothing purged[/muted]')
            return 0
        return 0 if _purge_keys([rows[0][0]]) else 1
    candidates = [row for row in rows if row[1] == 'stale']
    if not candidates:
        console.print('[muted]no stale keys — every attributed key belongs to a live account[/muted]')
        return 0
    if not apply:
        console.print(f'[muted]{len(candidates)} stale key(s); add [accent]--apply[/accent] to work '
                      'them one at a time[/muted]')
        return 0
    console.print(f'[accent]{len(candidates)}[/accent] stale key(s) — per key: '
                  '[accent]p[/accent]urge · [accent]s[/accent]kip · [accent]q[/accent]uit')
    drop: list[str] = []
    for candidate, _klass, note in candidates:
        console.print(f'  [accent]{candidate[:16]}…[/accent]  {note}')
        choice = console.input('  [accent]p/s/q[/accent] > ').strip().lower()[:1]
        if choice == 'q':
            break
        if choice != 'p':
            console.print('  [muted]skipped[/muted]')
            continue
        drop.append(candidate)
    if not drop:
        console.print('[muted]nothing purged[/muted]')
        return 0
    return 0 if _purge_keys(drop) else 1


def _purge_keys(keys: list[str]) -> bool:
    """Drop *keys* through the crypto package (every enc-key.json write lives there)."""
    count = revoke_keys(keys)
    if not count:
        return False
    _purge_after(count)
    return True


@register(requires='admin',
          help_text='Administer accounts, invite requests and enc-key entries (via sudo admin CLI).')
def users(action: Literal['list', 'process-requests', 'add', 'change', 'enable', 'disable',
                          'remove', 'purge', 'redeploy'] = 'list',
          identity: str = '', profile: Literal['reader', 'contributor', 'maintainer', 'admin'] = 'reader',
          apply: bool = False) -> int:
    """Administer accounts on the authorization map + the auth service.

    The whole command is ``admin``-floored and the account verbs re-execute the admin CLI
    under ``sudo`` (the SoR + admin socket are root-only). There is no reader/maintainer
    tier here — a web shell cannot get sudo, so nothing runs over the web.

    ``purge`` is the exception to the sudo shape: it *reads* the roster under sudo but does
    its work in **your checkout**, on ``keys/enc-key.json``, as you — because that file is
    the repo's, not the host's, and the change has to be committed and pushed like any
    other. It classifies every authorised key against the roster (via the ``owners``
    attribution ``user-authorize`` records) and offers the stale ones. Your own key is never
    a candidate, and an unattributed one is only ever purged by naming it.

    Args:
        action:   list (roster + pending + the invite-request queue), process-requests
                  (walk the queue interactively — accept / ignore / dismiss each),
                  add (map entry — ``@email`` also provisions + mints an invite; a bare
                  os-login is local-only), change (reassign a profile), enable / disable
                  (web SRP state), remove (drop the account/entry), purge (report — or with
                  ``--apply`` work — the enc-key entries whose owner is gone), redeploy
                  (re-assert the per-user host layer and re-lay every collaborator's git
                  hooks — takes no identity, and drops live shells).
        identity: a web email (``@``) or a local OS login for the account verbs; for
                  ``purge``, one public key (hex) to consider instead of the whole file.
                  Not used by list / process-requests / redeploy.
        profile:  the profile to assign (add / change). ``admin`` is valid only for a
                  local os-login, never a web account.
        apply:    ``purge`` only — actually remove, rather than report what it would offer.
    """
    if action == 'list':
        return _sudo_admin('list')                     # roster + pending + invite-request queue

    if action == 'process-requests':
        return _process_requests()                     # interactive: accept / ignore / dismiss

    if action == 'purge':
        # Not an account verb and not a host verb: a repo verb. It edits keys/enc-key.json
        # in this checkout, so it runs as the operator (the roster read is the only sudo
        # part) and leaves the commit to them.
        return _purge(identity, apply)

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

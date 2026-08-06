#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The collaborator roster — `/etc/euler/roster/users.json`.

A slug-keyed record of who exists and the X25519 public key each of them holds: the registry
`key-rekey` re-issues against, `key-split` seals to, and `msg send` builds its recipient menu
from. **Host state, read by everyone and written by maintainers**, which is the shape those
three readers actually need — the registry it replaced was an admin-plane read behind `sudo`,
and a web shell can never obtain that.

It was briefly a *tracked* file, which fixed the reading and broke the writing. `users` is
admin-gated and runs under `sudo`, but `user-authorize` and `key-split` are **maintainer**
commands: a maintainer granting from their web shell wrote the tracked file in their own clone,
on their own branch, where it reached nobody until a pull request that nobody opened — and
collided with the operator's copy at the next sync. One file both floors can write needs to
live where both floors can write it.

**Who may write it, and why that matters.** `/etc/euler/roster/` is `root:euler-maint 2775`
(setgid, so new files inherit the group) and the file is `0664` — world-readable, writable by
`euler-maint`, whose membership the account verbs keep at maintainer-and-above. The floor is
not tidiness: `public_key` is the one field here that is *used* rather than displayed —
:func:`~solver.crypto.keys._recipient_key` reads it to decide what a half gets sealed to — so
whoever can write it can redirect a future grant to a key they hold. Combined with host read
access to the share (`solver.crypto.config` `share_file`) that is the whole master key, which
is why the group must be people who already have it. Every other field is advisory.

**Public keys only. No key material.** Half the master key used to live here too, on the
argument that a single share of a 2-of-2 split is a uniformly random point and reveals nothing.
That is true and it was still wrong while this file was tracked: the repository is *public*, so
a half anybody can clone is not a second factor.

**No decisions.** `profile` is a **mirror for display and menus**; the system of record is
`/etc/euler/authorizations.json` beside it, root-owned, and every `rank()` comparison still
reads that. The `euler-maint` group is a write-ACL for advisory data, not a second copy of the
ladder: a stale member can write public keys and dates on a host they still have an account on,
and nothing else.

**No e-mail addresses.** Records are keyed by :func:`~solver.auth.identity.system_slug`, the
same `u`+hash the uid, home, socket and branch already use — the standing decision not to
publish who a collaborator is. The spool routes by that slug too (`box_of` leaves a non-address
unchanged), so a slug-keyed roster is enough to address a message, and the slug → identity
mapping stays in `authorizations.json`.

**Lifecycle: acts, not states.** The stamps here (`invited`, `provisioned`, `key_issued`,
`removed`) record what the **operator did**, dated at the moment it did it. They cannot drift,
because nothing but the operator writes them. The states a *user* drives (registration) and
the states enforcement depends on (`disabled`) deliberately stay on the host and are joined in
at display time: a mirror of `disabled` reading `active` for a locked-out account is the kind
of stale copy that gets trusted.

The accounts that predate this file were migrated once, in August 2026, and their acts dated
from what the host could still show — the registration record for `invited` / `provisioned`,
the enc-key file's mtime for `key_issued` — falling back to the migration's own clock where
nothing could be deduced. An approximate date on an act that certainly happened beats an empty
field, which reads as "never".

**Writers**, all of them account acts and none of them a service: `users add` / `change` /
`remove` (the operator), and `user-authorize` / `key-split` (any maintainer, recording the key
they just sealed to). Writes are whole-file and atomic — a temp file in the same directory,
then `os.replace` — because several maintainers share one file and a half-written roster reads
as "nobody holds a key", which is what a rotation would act on.

Stdlib-only and free of any :mod:`solver.config` dependency, so :mod:`solver.crypto` (which
is on the git-filter path) and :mod:`solver.web.msg` (stdlib-only importable) can both read it.
"""
from __future__ import annotations

__all__ = ['ROSTER_FILE_ENV', 'Roster', 'UserEntry', 'public_keys', 'read_roster',
           'roster_path', 'slug_of', 'slugs', 'stamp', 'upsert', 'user_entry', 'write_roster']

import os
from datetime import datetime, timezone
from json import dumps, loads
from pathlib import Path
from tempfile import mkstemp
from typing import Any, Literal, TypedDict, cast

from solver.auth.identity import system_slug
from solver.config.paths import repo_root

#: Environment override for the roster's location (tests, and any machine that keeps it
#: elsewhere).
ROSTER_FILE_ENV: str = 'EULER_ROSTER_FILE'

#: The deployed location: its own directory under `/etc/euler`, because the *directory* is
#: what has to be group-writable — an atomic replace writes a temp file beside the target and
#: renames over it, which needs write permission on the directory, not the file. A
#: group-writable file in a root-owned directory would force truncate-and-rewrite in place,
#: and a crash mid-write would leave an empty roster: "nobody holds a key", which is what the
#: next rotation would act on.
_SYSTEM_ROSTER: Path = Path('/etc/euler/roster/users.json')

#: The schema version, so a reader can refuse a file it does not understand rather than
#: guessing at it. Bump it only for a change a current reader could misread.
VERSION: int = 1


class UserEntry(TypedDict, total=False):
    """One collaborator, as the repository records them.

    Every field is optional: an entry is built up by the acts that touch it (an invite has no
    public key yet, a local os-login is never provisioned), and a reader must cope with any
    subset. `profile` is a **mirror** — see the module docstring.
    """

    public_key: str                      # X25519 public key hex, or '' — checkable, so safe here
    scope: Literal['web', 'local']       # a web account with an instance, or a bare os-login
    profile: str                         # MIRROR of /etc/euler/authorizations.json; never a gate
    invited: str                         # operator acts, ISO-8601 UTC, immutable once written
    provisioned: str
    key_issued: str                      # when the master key was last issued to `public_key`
    removed: str | None                  # the date they were removed, or null while they are not


class Roster(TypedDict, total=False):
    """The whole file: a version and the slug-keyed records."""

    version: int
    users: dict[str, UserEntry]


def stamp() -> str:
    """UTC now in ISO-8601 seconds — how every act in this file is dated."""
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def roster_path() -> Path:
    """Where the roster lives: `$EULER_ROSTER_FILE`, the deployed host, or this machine.

    The same three-step resolution the share file uses, and for the same reason — one machine,
    one answer, whether the caller is a web service running from `/opt/euler/venv` or a shell
    in somebody's clone:

    1. **`$EULER_ROSTER_FILE`** — the tests, and any machine that keeps it elsewhere.
    2. **`/etc/euler/roster/users.json`** when `/etc/euler` exists: a deployed host.
    3. **`~/.euler/roster.json`** otherwise — a plain checkout with no deployed tier, where
       the machine-local dot-directory beside the repo is already where such state lives.

    The *parent* of the deployed directory is probed rather than the file, so a first write on
    a deployed host lands in the deployed place rather than inventing a second copy in `~`.
    """
    override: str = os.environ.get(ROSTER_FILE_ENV, '').strip()
    if override:
        return Path(override)
    if _SYSTEM_ROSTER.parent.parent.is_dir():
        return _SYSTEM_ROSTER
    root: Path = repo_root()
    return root.parent / f'.{root.name}' / 'roster.json'


def read_roster() -> Roster:
    """The roster, or an empty one — this never raises and never reports a problem.

    Absent, unreadable, unparseable and *from a future version* all read as empty, because
    every caller's fallback is the same and better: ask the host. A roster is a convenience
    that removes a `sudo` prompt, so a bad one must degrade to the old path rather than break
    a command. What must never happen is a *wrong* answer, and it cannot: everything here is
    checked by its consumer (a public key seals or it does not; a share verifies or it does
    not) or is advisory to begin with.
    """
    try:
        data = cast(dict[str, Any], loads(roster_path().read_text()))
    except (OSError, ValueError, TypeError):
        return {'version': VERSION, 'users': {}}
    if not isinstance(data, dict) or int(data.get('version', 0)) > VERSION:
        return {'version': VERSION, 'users': {}}
    users = data.get('users')
    return {'version': VERSION,
            'users': {str(slug): cast(UserEntry, entry)
                      for slug, entry in (users or {}).items() if isinstance(entry, dict)}}


#: The order a record's fields are written in: who they are, then what was done to them **in
#: the order it happens**. Not alphabetical — this file is read by people, and a lifecycle
#: listed `invited → provisioned → key_issued → removed` can be checked at a glance (each date
#: should be no earlier than the one above it), where `invited, key_issued, provisioned,
#: removed` cannot. Anything not named here is written after, in the order it arrived, so an
#: older or newer schema's fields survive a round trip.
_FIELD_ORDER: tuple[str, ...] = ('public_key', 'scope', 'profile',
                                 'invited', 'provisioned', 'key_issued', 'removed')


def _ordered(entry: UserEntry) -> UserEntry:
    """One record with its fields in :data:`_FIELD_ORDER` — the shape a reader expects."""
    known = {key: entry[key] for key in _FIELD_ORDER if key in entry}       # type: ignore[literal-required]
    return cast(UserEntry, known | {key: value for key, value in entry.items() if key not in known})


def _record_order(item: tuple[str, UserEntry]) -> tuple[bool, str]:
    """Sort key: **local logins first**, then web slugs, each alphabetically.

    Not a cosmetic choice. The local entries are the operators — the accounts that hold the
    master key and run the verbs that write this file — and the web ones are the roll they
    administer. Putting the short list of people who *act* above the longer list of people
    acted upon is what makes the file read top-down. Alphabetical within each group keeps a
    one-record change to a one-record diff.
    """
    slug, entry = item
    return entry.get('scope') != 'local', slug


def write_roster(roster: Roster) -> Path:
    """Serialise the roster and return the path written — for the caller to commit.

    Records in :func:`_record_order`, fields in lifecycle order, and a trailing newline: this
    file is reviewed in diffs and merged like any other tracked text, so a stable order is
    what keeps a one-field change to a one-line diff. It is also why the order lives here
    rather than at the call sites — `upsert` merges, so without a canonical order every new
    field would land wherever it was first written, and a shape somebody arranged by hand
    would survive exactly until the next grant.

    **Atomic**, because several maintainers share one file: the body goes to a temp file in
    the same directory and is renamed over the target, so a reader never sees a half-written
    roster and a crash mid-write cannot leave an empty one. `0664` and the directory's setgid
    group, which is what lets the next maintainer replace it in turn.

    Raises:
        OSError: If the file cannot be written — most likely a caller who is not in
            `euler-maint`. Callers that have already acted (a grant is sent by the time it
            records) report it rather than failing the act.
    """
    path: Path = roster_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    body: Roster = {'version': VERSION,
                    'users': {slug: _ordered(entry) for slug, entry
                              in sorted((roster.get('users') or {}).items(), key=_record_order)}}
    handle, staged = mkstemp(dir=path.parent, prefix=f'.{path.name}.')
    try:
        with os.fdopen(handle, 'w', encoding='utf-8') as stream:
            stream.write(dumps(body, indent=2, sort_keys=False) + '\n')
        os.chmod(staged, 0o664)               # the group writes it next; setgid gave it the group
        os.replace(staged, path)
    except BaseException:
        Path(staged).unlink(missing_ok=True)
        raise
    return path


# ==================================================================================================================== #
#                                               users
# ==================================================================================================================== #
def user_entry(identity: str) -> UserEntry | None:
    """The record for *identity* — an e-mail or an already-slugged name — or None."""
    return read_roster().get('users', {}).get(slug_of(identity))


def slug_of(identity: str) -> str:
    """The roster key for *identity*: a slug stays itself, an address becomes its slug.

    Both forms reach this file — the operator types an address, a command that already has a
    box key passes the slug — and collapsing them here means no caller has to know which it
    holds. Matches :func:`solver.web.msg.identity.box_of` exactly, which is what lets a roster
    key be used as a message recipient unchanged.
    """
    name = identity.strip().lower()
    return system_slug(name) if '@' in name else name


def upsert(identity: str, **fields: str | None) -> Path:
    """Merge *fields* into *identity*'s record and write the file; returns the path.

    Merge rather than replace: the acts that touch a record arrive at different times from
    different verbs (an invite, then a provision, then a key), and each knows only its own
    field. Passing an empty string clears a field — `removed=''` is how a re-invite un-retires
    somebody — but a field simply omitted is never disturbed.
    """
    roster: Roster = read_roster()
    users: dict[str, UserEntry] = roster.get('users') or {}
    entry: UserEntry = dict(users.get(slug_of(identity)) or {})     # type: ignore[assignment]
    entry.update(cast(UserEntry, {key: value for key, value in fields.items()}))
    users[slug_of(identity)] = entry
    roster['users'] = users
    return write_roster(roster)


def public_keys() -> dict[str, str]:
    """`{slug: public_key}` for every live record that has one.

    The registry a rotation re-issues against and `key-split` seals to. Removed records are
    left out: their key was real, but issuing to somebody the operator retired is the one
    mistake this list must not make easy.
    """
    return {slug: str(entry.get('public_key', ''))
            for slug, entry in (read_roster().get('users') or {}).items()
            if entry.get('public_key') and not entry.get('removed')}


def slugs(scope: str = '') -> list[str]:
    """Every live slug, optionally filtered to a scope (`web` / `local`), sorted.

    What a recipient menu is built from. A `web` record has an instance and therefore a
    mailbox; a `local` one is the operator at a terminal, who reads the spool but has nothing
    to push a badge to.
    """
    return sorted(slug for slug, entry in (read_roster().get('users') or {}).items()
                  if not entry.get('removed') and (not scope or entry.get('scope') == scope))

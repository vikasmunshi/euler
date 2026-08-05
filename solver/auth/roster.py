#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The tracked collaborator roster — `users/users.json`.

The one thing about collaborators that lives **in the repository**: a slug-keyed record of who
exists and the X25519 public key each of them holds. It is tracked, so every clone has it and
no reader needs `sudo` — which is the whole reason it exists. The registry it replaces was an
admin-plane read behind `sudo`, and a web shell can never obtain that: `key-rekey` refused to
rotate when it could not read the roster, `key-split` had to be handed a public key by hand,
and `msg send`'s recipient menu quietly shrank to two words.

**Public keys only. No key material.** Half the master key used to live here too, on the
argument that a single share of a 2-of-2 split is a uniformly random point and reveals nothing.
That is true and it was still wrong: this repository is *public*, so a half anybody can clone
is not a second factor, and the sealed message plus the recipient's private key was the whole
of the secret. It now lives on the host (`solver.crypto.config` `share_file`), where the two
halves are protected by different things again.

**What may be in here, and what may not.** Every collaborator can write their own clone (`!` is
contributor-floored, and their per-user service serves that same clone). Two rules follow, and
everything below obeys them:

1. **Facts that verify themselves, or nothing.** A public key is checkable — it either unwraps
   what was sealed to it or it does not. Tamper with one in your own clone and you break only
   yourself. Nothing here is ever *believed*.
2. **No decisions.** `profile` is a **mirror for display and menus**; the system of record is
   `/etc/euler/authorizations.json`, root-owned and outside the repo, and every `rank()`
   comparison still reads that. A tracked profile that gated anything would be a one-line
   privilege escalation for the person whose own clone it is read from.

**No e-mail addresses.** Records are keyed by :func:`~solver.auth.identity.system_slug`, the
same `u`+hash the uid, home, socket and branch already use — the project's standing decision
not to publish who a collaborator is. The spool routes by that slug too (`box_of` leaves a
non-address unchanged), so a slug-keyed roster is enough to address a message, and the
slug → identity mapping stays on the host where it belongs.

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

**Single writer.** The operator's `users` / `user-authorize` / `key-split` / `key-rekey` paths
write this file and commit it; **no service and no per-user shell ever writes it**. That is
what keeps it out of the failure the tracked enc-key file used to have — that file had one
writer per machine, so every rotation dirtied it in every clone and the merges collided. One
writer and many readers is the pattern git handles without ceremony.

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
from typing import Any, Literal, TypedDict, cast

from solver.auth.identity import system_slug
from solver.utils.repo_root import repo_root

#: Environment override for the roster's location (tests, and any service pointed elsewhere).
ROSTER_FILE_ENV: str = 'EULER_ROSTER_FILE'

#: Where the roster lives in the checkout. A directory of its own rather than a file at the
#: root: it is neither solver code nor a solution, and `users/` says what it is.
_REPO_PATH: tuple[str, str] = ('users', 'users.json')

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
    """The roster file: `$EULER_ROSTER_FILE`, else `users/users.json` in the checkout.

    Anchored at the repo root rather than at `__file__`, for the reason the share file was:
    the deployed web tier runs this code from `/opt/euler/venv`, where `__file__` is the
    installed copy and not the collaborator's tree — and one tree's roster answered to every
    user would be worse than no roster at all.
    """
    override: str = os.environ.get(ROSTER_FILE_ENV, '').strip()
    return Path(override) if override else repo_root().joinpath(*_REPO_PATH)


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

    Writing does **not** commit: the paths that write it know whether they can (see the module
    docstring on the single writer), and a command that silently commits is a command that
    surprises somebody mid-rebase.
    """
    path: Path = roster_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    body: Roster = {'version': VERSION,
                    'users': {slug: _ordered(entry) for slug, entry
                              in sorted((roster.get('users') or {}).items(), key=_record_order)}}
    path.write_text(dumps(body, indent=2, sort_keys=False) + '\n')
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

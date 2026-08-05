#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""One-shot migration: finish moving the public-key registry into the tracked roster.

Run **once**, under sudo, on the deployed host. Delete it afterwards — it is a migration,
not a tool, and everything it does is done by the ordinary account verbs from here on.

Two halves of one change:

1. **Backfill `users/users.json`** to the shape it was designed for — profile, scope, the
   operator's dated acts, and the public key — for the accounts that predate it. Every act
   recorded here certainly happened; only the dates were never written down, so each is dated
   from the closest thing the host can still show, and from the migration's own clock when
   nothing can:

   - `invited`, `provisioned` ← **the SRP record's `created`**. They were invited and
     provisioned before they could possibly register, so registration is a true upper bound
     rather than a date invented for the field.
   - `key_issued` ← **the mtime of their `~/.euler/enc-key.json`**. That file is written when
     a grant is taken, so its mtime *is* when they last received the key.
   - `removed` ← **null**. Nobody being migrated has been removed.
   - anything undeducible ← **the migration timestamp**. An approximate date on an act that
     certainly happened beats an empty field, which reads as "never".

   A **local** os-login gets neither `invited` nor `provisioned`: those acts did not happen
   late, they did not happen at all — a bare login is a map entry with no invite and no
   instance. It does get a public key, since its home holds an enc-key file like any other.

   The earlier revision of this script wrote a `created` field that is not part of the
   schema; it is removed here.

2. **Strip `public_key` from `/var/lib/euler-auth/users.json`.** That store holds the login
   secrets; a second copy of the public keys only created a pair that could disagree. The
   code no longer reads or writes the field — this removes what the old code left behind.

Idempotent: run it twice and the second run reports nothing to do. It never writes a key it
cannot read from the holder's own enc-key file, and it never removes a roster entry.

    sudo .venv/bin/python scripts/ops/migrate-roster.py [--dry-run]
"""
from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from solver.auth import roster                                    # noqa: E402  (after sys.path)
from solver.auth.identity import system_slug                      # noqa: E402

AUTHZ = Path(os.environ.get('EULER_AUTHZ_FILE', '/etc/euler/authorizations.json'))
AUTH_STORE = Path(os.environ.get('EULER_AUTH_STATE_DIR', '/var/lib/euler-auth')) / 'users.json'


def _load(path: Path) -> dict[str, Any]:
    """Read a JSON object, or an empty one when it is absent/unreadable."""
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _enc_key_file(name: str) -> Path:
    """Where *name*'s enc-key file lives — their home is named for their slug (or login)."""
    return Path(f'/home/{name}') / '.euler' / 'enc-key.json'


def _public_key_of(name: str) -> str:
    """The public key in *name*'s own enc-key file, or `''` when there is not exactly one.

    Their file holds two records — `verify` and the master key wrapped to their public key —
    so the entry that is not `verify` *is* the key. No unwrapping, no private key, no master
    key: this reads a name, not a secret. It is also the only place the key can be read from,
    since `~/.euler/id` is vault-encrypted and that vault opens only in its owner's session.

    Local logins included, deliberately: a bare os-login has a home and an enc-key file like
    anyone else, and the operator — the one account that is certainly a key holder — is one.
    """
    data = _load(_enc_key_file(name))
    keys = [key for key in data if key != 'verify' and len(str(key)) == 64]
    return str(keys[0]) if len(keys) == 1 else ''


def _key_issued_at(name: str) -> str:
    """When *name* last took a grant: the mtime of the enc-key file writing one produces."""
    try:
        stamp = _enc_key_file(name).stat().st_mtime
    except OSError:
        return ''
    return datetime.fromtimestamp(stamp, UTC).isoformat(timespec='seconds')


def backfill_roster(dry_run: bool, now: str) -> int:
    """Bring every account the host knows about up to the roster's designed shape."""
    profiles: dict[str, str] = {str(name).strip().lower(): str(profile)
                                for name, profile in (_load(AUTHZ).get('users') or {}).items()}
    accounts: dict[str, dict[str, Any]] = _load(AUTH_STORE).get('users') or {}
    if not profiles and not accounts:
        print(f'nothing to read: neither {AUTHZ} nor {AUTH_STORE} is readable — are you root?')
        return 1
    changed = 0
    for identity in sorted(set(profiles) | set(accounts)):
        scope = 'web' if '@' in identity else 'local'
        slug = system_slug(identity) if scope == 'web' else identity
        fields: dict[str, str | None] = {'scope': scope, 'removed': None}
        if identity in profiles:
            fields['profile'] = profiles[identity]                # the mirror; the host decides
        if public_key := _public_key_of(slug):
            fields['public_key'] = public_key                     # only what they actually hold
            fields['key_issued'] = _key_issued_at(slug) or now
        if scope == 'web':
            # Invited and provisioned before they could possibly have registered, so the
            # registration date is a true upper bound; the migration clock where even that
            # is missing (an invite nobody has taken up yet).
            when = str(accounts.get(identity, {}).get('created', '')) or now
            fields['invited'] = fields['provisioned'] = when
        entry = roster.user_entry(slug) or {}
        stale_created = 'created' in entry                        # written by an earlier revision
        if not stale_created and all(entry.get(key) == value for key, value in fields.items()):
            continue
        print(f'  {slug}: {", ".join(sorted(fields))}'
              f'{" (dropping created)" if stale_created else ""}')
        changed += 1
        if not dry_run:
            if stale_created:
                _drop_field(slug, 'created')
            roster.upsert(slug, **fields)
    print(f'{changed} roster record(s) {"would be " if dry_run else ""}updated '
          f'({roster.roster_path()})')
    if changed and not dry_run:
        print('  → commit and push it: the roster is tracked')
    return 0


def _drop_field(slug: str, field: str) -> None:
    """Remove one field from one record — `upsert` merges, so this is how a key leaves."""
    data = roster.read_roster()
    entry: dict[str, Any] = dict(data.get('users', {}).get(slug) or {})
    entry.pop(field, None)
    data.setdefault('users', {})[slug] = cast(roster.UserEntry, entry)
    roster.write_roster(data)


def strip_public_keys(dry_run: bool) -> int:
    """Remove the `public_key` field from every record in the auth service's own store."""
    data = _load(AUTH_STORE)
    accounts: dict[str, dict[str, Any]] = data.get('users') or {}
    holders = [email for email, record in accounts.items() if 'public_key' in record]
    if not holders:
        print(f'{AUTH_STORE}: no public_key fields left — nothing to strip')
        return 0
    print(f'{AUTH_STORE}: stripping public_key from {len(holders)} record(s)')
    if dry_run:
        return 0
    for email in holders:
        accounts[email].pop('public_key', None)
    # Written the way the store writes it: same shape, same 0600, atomic replace so a crash
    # cannot leave the verifier database truncated.
    temporary = AUTH_STORE.with_suffix('.migrating')
    temporary.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    os.chmod(temporary, 0o600)
    stat = AUTH_STORE.stat()
    os.chown(temporary, stat.st_uid, stat.st_gid)                 # stays euler-auth's own file
    os.replace(temporary, AUTH_STORE)
    print('  → done; euler-auth re-reads the file per operation, so no restart is needed')
    return 0


def main(argv: list[str]) -> int:
    dry_run = '--dry-run' in argv
    now = roster.stamp()                    # one timestamp for the whole run, so it reads as one act
    if dry_run:
        print('dry run — nothing will be written\n')
    print(f'roster:     {roster.roster_path()}')
    print(f'auth store: {AUTH_STORE}')
    print(f'policy:     {AUTHZ}')
    print(f'undeducible dates will read {now}\n')
    return backfill_roster(dry_run, now) or strip_public_keys(dry_run)


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))

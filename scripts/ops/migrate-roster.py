#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""One-shot migration: finish moving the public-key registry into the tracked roster.

Run **once**, under sudo, on the deployed host. Delete it afterwards — it is a migration,
not a tool, and everything it does is done by the ordinary account verbs from here on.

Two halves of one change:

1. **Backfill `users/users.json`** for the accounts that predate it. `users set-keys` (now
   gone) recorded only a public key and a scope, so the records are missing the profile
   mirror and every date. What can be filled honestly is filled: the profile from
   `/etc/euler/authorizations.json`, the scope, and `created` — the date the host's own SRP
   record was written. The lifecycle stamps a grant writes (`key_issued`) and the ones an
   invite writes (`invited`, `provisioned`) are **not** invented: those acts happened before
   anything recorded them, and a plausible-looking wrong date is worse than an absent one.

   `created` is a host fact rather than an operator act, which is a line the roster otherwise
   holds. It qualifies on the property that line is really about: it is **immutable and
   dateable**, so it cannot drift into a lie. `disabled` and registration state are mutable,
   and stay on the host where they are read fresh.

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
from pathlib import Path
from typing import Any

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


def _public_key_of(slug: str) -> str:
    """The public key in *slug*'s own enc-key file, or `''` when there is not exactly one.

    Their file holds two records — `verify` and the master key wrapped to their public key —
    so the entry that is not `verify` *is* the key. No unwrapping, no private key, no master
    key: this reads a name, not a secret. It is also the only place the key can be read from,
    since `~/.euler/id` is vault-encrypted and that vault opens only in its owner's session.
    """
    data = _load(Path(f'/home/{slug}') / '.euler' / 'enc-key.json')
    keys = [key for key in data if key != 'verify' and len(str(key)) == 64]
    return str(keys[0]) if len(keys) == 1 else ''


def backfill_roster(dry_run: bool) -> int:
    """Fill in profile, scope and `created` for every account the host knows about."""
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
        fields: dict[str, str] = {'scope': scope}
        if identity in profiles:
            fields['profile'] = profiles[identity]                # the mirror; the host decides
        if created := str(accounts.get(identity, {}).get('created', '')):
            fields['created'] = created
        if scope == 'web' and (public_key := _public_key_of(slug)):
            fields['public_key'] = public_key                     # only what they actually hold
        entry = roster.user_entry(slug) or {}
        if all(entry.get(key) == value for key, value in fields.items()):
            continue
        print(f'  {slug}: {", ".join(f"{k}={v[:16]}" for k, v in sorted(fields.items()))}')
        changed += 1
        if not dry_run:
            roster.upsert(slug, **fields)
    print(f'{changed} roster record(s) {"would be " if dry_run else ""}updated '
          f'({roster.roster_path()})')
    if changed and not dry_run:
        print('  → commit and push it: the roster is tracked')
    return 0


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
    if dry_run:
        print('dry run — nothing will be written\n')
    print(f'roster:     {roster.roster_path()}')
    print(f'auth store: {AUTH_STORE}')
    print(f'policy:     {AUTHZ}\n')
    return backfill_roster(dry_run) or strip_public_keys(dry_run)


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))

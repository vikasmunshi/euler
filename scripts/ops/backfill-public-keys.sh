#!/usr/bin/env bash
# Backfill users.json with each collaborator's X25519 public key — the registry `key-rekey`
# re-issues a rotated master key to.
#
#   sudo bash scripts/ops/backfill-public-keys.sh [--apply] [identity ...]
#
# `user-authorize` records the key as it issues one, but only when it can reach the auth
# admin plane — and a **web shell cannot sudo**, so every grant made from a browser leaves
# the registry empty. Nothing breaks until the next rotation, at which point an account with
# no registered key cannot be re-issued to and loses access. `key-rekey` names those accounts
# before it asks, but the cheaper answer is not to have any.
#
# **Where the keys come from.** Each holder's own `~/.euler/enc-key.json` has exactly two
# records: `verify`, and their public key. The one that is not `verify` is the answer — no
# unwrapping, no private keys, no master key anywhere in this script. (Their `~/.euler/id`
# could not serve: it is vault-encrypted, and the vault opens only inside their own session.)
#
# Web accounts only: `users.json` holds the SRP database, and a local os-login has no record
# in it. The operator's own key is not registered anywhere and does not need to be — they
# hold the master key, so a rotation starts with them.
#
# THROWAWAY: this exists because the registry was added after the accounts were. Once every
# account has a key, `user-authorize` keeps it that way and this script has nothing to do.
#
# Author: Vikas Munshi <vikas.munshi@gmail.com>
# Copyright (c) 2026. All rights reserved.
# Licensed under the MIT License.
set -uo pipefail

AUTHZ_FILE="${EULER_AUTHZ_FILE:-/etc/euler/authorizations.json}"
VENV_PYTHON="${EULER_VENV_PYTHON:-/opt/euler/venv/bin/python}"
APPLY=0
WANTED=()

for arg in "$@"; do
    case "${arg}" in
        --apply) APPLY=1 ;;
        -h | --help | help) sed -n '2,26p' "$0"; exit 0 ;;
        -*) echo "Error: unknown option: ${arg}" >&2; exit 2 ;;
        *) WANTED+=("${arg}") ;;
    esac
done

if [[ ${EUID} -ne 0 ]]; then
    echo "Error: run under sudo — it reads other users' homes and writes the SoR." >&2
    exit 1
fi
if [[ ! -r "${AUTHZ_FILE}" ]]; then echo "Error: cannot read ${AUTHZ_FILE}" >&2; exit 1; fi
if [[ ! -x "${VENV_PYTHON}" ]]; then echo "Error: no venv python at ${VENV_PYTHON}" >&2; exit 1; fi
if [[ ${APPLY} -ne 1 ]]; then echo "DRY RUN — add --apply to write"; fi

# Every web identity on the map (an os-login has no users.json record to write to).
mapfile -t IDENTITIES < <(python3 -c "
import json, sys
users = json.load(open('${AUTHZ_FILE}')).get('users', {})
print('\n'.join(sorted(name for name in users if '@' in name)))
")
if [[ ${#WANTED[@]} -gt 0 ]]; then IDENTITIES=("${WANTED[@]}"); fi

registered=0
missing=0
for identity in "${IDENTITIES[@]}"; do
    # The slug is `u` + the first 6 hex of sha1(lowercased identity) — solver.auth.identity's
    # system_slug, computed here with the standard library so this script needs no imports
    # from the package it is repairing.
    slug="$(python3 -c "
import hashlib, sys
print('u' + hashlib.sha1(sys.argv[1].strip().lower().encode()).hexdigest()[:6])" "${identity}")"
    home="$(getent passwd "${slug}" | cut -d: -f6)"
    enc_key="${home:-/nonexistent}/.euler/enc-key.json"

    public_key="$(python3 -c "
import json, sys
try:
    data = json.load(open(sys.argv[1]))
except OSError:
    raise SystemExit('')
keys = [k for k in data if k != 'verify' and len(k) == 64]
print(keys[0] if len(keys) == 1 else '')" "${enc_key}" 2>/dev/null)"

    if [[ -z "${public_key}" ]]; then
        echo "  ${identity} (${slug}): no key in ${enc_key} — they must run \`user\` and be issued one"
        missing=$((missing + 1))
        continue
    fi
    echo "  ${identity} (${slug}): ${public_key:0:16}…"
    if [[ ${APPLY} -eq 1 ]]; then
        if ! "${VENV_PYTHON}" -P -m solver.web.auth.admin set-key "${identity}" "${public_key}"; then
            echo "    FAILED to register — is euler-auth.service running?" >&2
            continue
        fi
    fi
    registered=$((registered + 1))
done

echo
if [[ ${APPLY} -eq 1 ]]; then
    echo "Registered ${registered} key(s); ${missing} account(s) still without one."
    echo "Verify with: solver \"users list\"  (or the roster's public_key column)"
else
    echo "Would register ${registered} key(s); ${missing} account(s) have none to register."
fi

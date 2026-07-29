#!/usr/bin/env bash
# Seed each collaborator's machine-local enc-key file from the (retiring) tracked one.
#
#   sudo bash scripts/ops/issue-enc-key.sh [--apply] [slug ...]
#
# One-off, for the move of the wrapped master key out of the repository. Until now
# `keys/enc-key.json` was tracked and held every authorised key; now each holder keeps two
# records of their own — `verify`, and the master key wrapped to their public key — at
# `~/.euler/enc-key.json`, and issuing one is a maintainer's `user-authorize` sending it
# through the message spool.
#
# This script does for the existing holders what `msg save` will do for every future one:
# it copies each collaborator's own entry out of the tracked file into their secrets dir.
# Nothing is wrapped or unwrapped here — the entry is already sealed to their public key,
# so this moves ciphertext and never sees a master key.
#
# **Run it before the tracked file is deleted.** After that there is nothing to copy from,
# and a collaborator whose file never arrived has to ask for it by message.
#
# THROWAWAY: delete this script once every collaborator is on their own file.
#
# Author: Vikas Munshi <vikas.munshi@gmail.com>
# Copyright (c) 2026. All rights reserved.
# Licensed under the MIT License.
set -uo pipefail

REPO="${EULER_REPO:-/home/vikas/euler}"
TRACKED="${REPO}/keys/enc-key.json"
APPLY=0
SLUGS=()

for arg in "$@"; do
    case "${arg}" in
        --apply) APPLY=1 ;;
        -h | --help | help) sed -n '2,20p' "$0"; exit 0 ;;
        -*) echo "Error: unknown option: ${arg}" >&2; exit 2 ;;
        *) SLUGS+=("${arg}") ;;
    esac
done
if [[ ${#SLUGS[@]} -eq 0 ]]; then
    SLUGS=(u0a68e0 uaa7d3c uc448f9 u3f9e97 u3cc4d2 u6ac7a5)
fi

if [[ ${EUID} -ne 0 ]]; then echo "Error: run under sudo (it writes other users' homes)." >&2; exit 1; fi
if [[ ! -r "${TRACKED}" ]]; then echo "Error: cannot read ${TRACKED}" >&2; exit 1; fi
if [[ ${APPLY} -ne 1 ]]; then echo "DRY RUN — add --apply to act"; fi

for slug in "${SLUGS[@]}"; do
    echo "── ${slug}"
    if ! id -u "${slug}" &> /dev/null; then echo "    no such user — skipped"; continue; fi
    home="$(getent passwd "${slug}" | cut -d: -f6)"
    group="$(id -gn "${slug}")"
    target="${home}/.euler/enc-key.json"

    # Their public key comes from their OWN private key, not from the file's attribution:
    # the key that has to open this payload is the one on their disk, and reading it from
    # there is the only way to be sure the two agree. A vault-encrypted id cannot be read
    # from here (it unlocks only in their session) — those fall back to the attribution map.
    payload="$(python3 - "${TRACKED}" "${home}" "${slug}" <<'PY'
import json, sys
tracked, home, slug = sys.argv[1], sys.argv[2], sys.argv[3]
data = json.load(open(tracked))
pub = ''
try:                                      # the attribution map, keyed by slug
    pub = data.get('owners', {}).get(slug, {}).get('key', '')
except AttributeError:
    pub = ''
if not pub or pub not in data:
    raise SystemExit('')
json.dump({'verify': data['verify'], pub: data[pub]}, sys.stdout, indent=2)
PY
)"
    if [[ -z "${payload}" ]]; then
        echo "    no entry for this slug in ${TRACKED} — they must request one by message"
        continue
    fi
    if [[ ${APPLY} -ne 1 ]]; then
        echo "    would write ${target} (2 records, 0600 ${slug}:${group})"
        continue
    fi
    install -d -o "${slug}" -g "${group}" -m 0700 "${home}/.euler"
    tmp="$(mktemp)"
    printf '%s\n' "${payload}" > "${tmp}"
    install -o "${slug}" -g "${group}" -m 0600 "${tmp}" "${target}"
    rm -f "${tmp}"
    echo "    wrote ${target}"
done

echo
echo "Done. Each collaborator should reconnect their web shell, then \`git-filter install\`"
echo "if their private solutions are still ciphertext. Only then delete keys/enc-key.json."

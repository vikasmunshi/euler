#!/usr/bin/env bash
# Collect the web services' journals and the live shells' state, read-only, for debugging.
#
#   scripts/ops/capture-journal.sh                                  # the last hour
#   scripts/ops/capture-journal.sh '2026-11-06 15:10' '2026-11-06 15:20'
#
# Arguments are journalctl's --since and --until, so '-15min' works too. One sudo prompt, and
# everything lands in one log under audit/logs/, through capture-run.sh: the journal of every
# loaded per-user instance, the auth, message and public-site services and Caddy; then, for each
# instance running now, its shells and any logout notice; then how many remember-me tokens are
# held. It changes nothing, and calls only running instances, because dialling a stopped
# instance's socket starts it. The log names collaborators, which is why audit/ is ignored by git.
set -uo pipefail

if [ "${1:-}" = '-h' ] || [ "${1:-}" = '--help' ]; then
    sed -n '2,11p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
    exit 0
fi
if [ "${1:-}" != '--inner' ]; then
    self="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"
    exec "$(dirname "${self}")/capture-run.sh" -- sudo bash "${self}" --inner "${1:--1 hour}" "${2:-now}"
fi

SINCE="$2"
UNTIL="$3"

section() { printf '\n######## %s\n' "$1"; }
journal() { journalctl -u "$1" --since "${SINCE}" --until "${UNTIL}" -o short-iso --no-pager; }
instances() { systemctl list-units 'euler-user@*.service' "$@" --plain --no-legend | awk '{print $1}'; }

for unit in $(instances --all); do
    section "${unit}"
    journal "${unit}"
done
for unit in euler-auth euler-msg euler-site euler-caddy; do
    section "${unit}.service"
    journal "${unit}.service"
done
section 'caddy: where access logs go'
grep -n -A4 -E '^\s*log\b' /etc/euler/Caddyfile || echo 'no log directive in the Caddyfile'

section 'running instances, now'
for unit in $(instances --state=active); do
    slug="${unit#euler-user@}"
    slug="${slug%.service}"
    for route in status logout-notice; do
        printf '%s /internal/%s: ' "${slug}" "${route}"
        curl -sS --max-time 5 --unix-socket "/run/euler/user-${slug}.sock" "http://localhost/internal/${route}"
        echo
    done
done

section 'remember-me tokens held, now (a count, nothing from the tokens)'
python3 -c "import json; print(len(json.load(open('/var/lib/euler-auth/remember.json'))))" \
    || echo 'no remember.json'

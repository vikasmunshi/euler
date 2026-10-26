#!/usr/bin/env bash
# Snapshot the evidence a change to the web host would destroy, before making it.
#
# For an incident, or ahead of a hardening release when you want to look back afterwards for
# signs of abuse: every Caddy reload overwrites autosave.json, a service restart rebinds the
# sockets in /run/euler, and the journal rotates. Captured: Caddy's saved, running and adapted
# configs; every euler unit's journal in full; the socket directory and its listeners; each
# home's ~/.euler and git hooks (names, owners, modes, recent changes — never contents); the
# euler groups and the firewall. A SHA256SUMS file makes later edits to the snapshot visible.
#
# Read-only on the host. Run as yourself (it calls sudo itself):
#
#   bash scripts/ops/capture-evidence.sh
#
# Output: audit/evidence-<timestamp>/ (0700, yours, ignored by git). It holds journal lines with
# collaborator addresses, so treat it as confidential and delete it once you have looked.

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT="${ROOT}/audit/evidence-$(date +%Y%m%d-%H%M%S)"
CADDY_STATE=/var/lib/euler-caddy/caddy
CADDY_ADMIN=/run/euler-caddy/admin.sock     # the admin API is unix-socket only (frontend.sh)

if [ "$(id -u)" -eq 0 ]; then
    echo "error: run as yourself, not under sudo (the script calls sudo itself)" >&2
    exit 2
fi

# ensure sudo
sudo true || exit 1

umask 077
mkdir -p "${ROOT}/audit" && mkdir "${OUT}" || exit 1
chmod 0700 "${OUT}"
echo "capturing evidence → ${OUT}"

# Run a command, keep its output (stdout + stderr) in <file>, and note the exit status in the index.
capture () {
    local file="$1"; shift
    bash -c "$*" > "${OUT}/${file}" 2>&1
    printf '%-26s rc=%-3s $ %s\n' "${file}" "$?" "$*" >> "${OUT}/INDEX.txt"
}

# Caddy: the config it last loaded, the config it is running now, and what the Caddyfile adapts to.
capture caddy-autosave.json   "sudo cat ${CADDY_STATE}/autosave.json"
capture caddy-autosave.stat   "sudo stat ${CADDY_STATE}/autosave.json"
capture caddy-running.json    "sudo curl -s -m 5 --unix-socket ${CADDY_ADMIN} http://localhost/config/"
capture caddyfile             "sudo cat /etc/euler/Caddyfile"
capture caddyfile-adapted.json "sudo caddy adapt --config /etc/euler/Caddyfile --adapter caddyfile"

# Journals, in full, for every euler unit (admin-API requests, logins, tickets, pushes).
capture journal-euler.txt     "sudo journalctl -u 'euler-*' --no-pager -o short-iso"
capture journal-disk.txt      "sudo journalctl --disk-usage; sudo journalctl --list-boots --no-pager | tail -5"

# The socket directory: what is there, and which process listens on each path.
capture run-euler.txt         "sudo ls -la --time-style=full-iso /run/euler /run/euler-adm /run/euler-msg"
capture run-euler-listeners.txt "sudo ss -xlnp | grep -E '/run/euler'"

# Tenant secrets dirs: presence, owners, modes and times — never contents.
capture tenant-euler-dirs.txt "sudo bash -c 'ls -la --time-style=full-iso /home/*/.euler'"
capture tenant-recent.txt     "sudo bash -c \"find /home/*/.euler /home/*/euler/.git/hooks -newermt '-30 days' -printf '%TY-%Tm-%Td %TH:%TM %M %u:%g %p\\n'\""

# Who belonged to which group, and the firewall, at snapshot time.
capture groups.txt            "getent group | grep -E '^euler'"
capture nftables.txt          "sudo nft list table inet euler"

# Integrity: a checksum of everything captured, so later edits to the snapshot would show.
(cd "${OUT}" && sha256sum -- * > SHA256SUMS)

sudo chown -R "$(id -u):$(id -g)" "${OUT}"
chmod -R go-rwx "${OUT}"
echo "done: $(find "${OUT}" -type f | wc -l) files — see ${OUT}/INDEX.txt"

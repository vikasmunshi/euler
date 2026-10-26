#!/usr/bin/env bash
# Capture the web host's security posture, read-only, into one 0600 file you own.
#
# What it records: status-web, the Caddyfile, the full nftables ruleset, every TCP/UDP and
# euler unix listener, sudoers, the euler users and groups, owners and modes under /etc/euler,
# /run/euler, /var/lib/euler*, /opt/euler and every home's ~/.euler, each euler unit's
# definition and `systemd-analyze security` score, the timers, and the last auth/edge journal
# lines. It changes nothing, and never prints a secret's *contents* — only names, owners and
# modes (the Caddyfile and the unit files hold no secrets).
#
# Run it as yourself, not under sudo: it calls sudo where it must, and the output stays yours.
#
#   bash scripts/ops/capture-host.sh [OUT]    (default: audit/host-capture.txt)
#
# Compare two captures with `diff` to see what a release changed. audit/ is ignored by git:
# a capture describes the host's defences and names its accounts.

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT=${1:-${ROOT}/audit/host-capture.txt}

if [ "$(id -u)" -eq 0 ]; then
    echo "error: run as yourself, not under sudo (the script calls sudo itself)" >&2
    exit 2
fi

# ensure sudo
sudo true || exit 1

umask 077
mkdir -p "$(dirname "$OUT")"
: > "$OUT"
echo "capturing output → $OUT"

run_cmd () {
  printf '\n===== $ %s\n' "$*"
  bash -c "$*" 2>&1
  printf -- '----- rc=%s\n' "$?"
}

# Every euler unit, loaded or not, instances included (euler-user@<slug>.*).
units () {
  { systemctl list-units 'euler-*' --all --plain --no-legend
    systemctl list-unit-files 'euler-*' --plain --no-legend
  } | awk '{print $1}' | sort -u
}

{
  run_cmd "date -Is; uname -a; id"
  run_cmd "git -C '${ROOT}' describe --tags --always; grep -h '^__version__' /opt/euler/venv/lib/python*/site-packages/solver/version.py 2>/dev/null"

  run_cmd "make -s -C '${ROOT}' status-web"

  # The edge
  run_cmd "sudo cat /etc/euler/Caddyfile"
  run_cmd "caddy version 2>/dev/null || /opt/euler/bin/caddy version"
  run_cmd "sudo nft list ruleset"
  run_cmd "sudo ss -tlnpu"
  run_cmd "sudo ss -xlnp | grep -i euler"

  # Who can do what as root
  run_cmd "sudo ls -la /etc/sudoers.d"
  run_cmd "sudo grep -rnv '^\s*#' /etc/sudoers /etc/sudoers.d | grep -v ':\s*$'"
  run_cmd "sudo -l"

  # Identities
  run_cmd "getent passwd | awk -F: '\$1 ~ /^euler/ || \$3 >= 1000' "
  run_cmd "getent group | awk -F: '\$1 ~ /^euler/ || \$3 >= 1000'"

  # Filesystem layout and modes (names only, never contents)
  run_cmd "sudo ls -laR /etc/euler | head -300"
  run_cmd "sudo ls -laR /run/euler | head -200"
  run_cmd "sudo find /var/lib/euler* -maxdepth 3 -printf '%M %u:%g %p\n' 2>/dev/null | head -200"
  run_cmd "sudo ls -la /opt/euler /opt/euler/venv /opt/euler/venv/bin | head -80"
  run_cmd "sudo find /opt/euler -perm -o+w ! -type l -printf '%M %u:%g %p\n' | head -50"
  run_cmd "sudo ls -la /home /home/*/ 2>&1 | head -200"
  run_cmd "sudo bash -c 'ls -la /home/*/.euler' 2>&1 | head -150"
  run_cmd "sudo bash -c \"find /home/*/euler -maxdepth 1 -name .git -prune -o -maxdepth 1 -perm -o+r -printf '%M %u:%g %p\\n'\" 2>/dev/null | head -60"

  # Units: definitions, drop-ins, hardening score
  for u in $(units); do
    run_cmd "systemctl cat '$u'"
  done
  for u in $(units); do
    case $u in *@.*) continue ;; esac  # templates cannot be analysed, their instances can
    run_cmd "systemd-analyze security '$u' --no-pager | tail -1"
  done
  run_cmd "systemctl list-timers 'euler-*' --all --no-pager"

  # Recent auth-relevant log lines (no request bodies are logged)
  run_cmd "sudo journalctl -u euler-auth -u euler-caddy -n 150 --no-pager -o short-iso"
} >> "$OUT"

chmod 0600 "$OUT"
echo "done: $(wc -l < "$OUT") lines"

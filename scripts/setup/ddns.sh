#!/usr/bin/env bash
# Dynamic DNS Updater (name.com A record) — host-scripted, for public edge access
# ================================================================================
#
# Keeps the edge's A record (e.g. euler.vikasmunshi.com) pointed at the host's current
# public IP, so the Caddy edge (scripts/setup/frontend.sh) stays reachable behind a
# changing ISP address. Replaces the "external updater" hand-wave in docs/tls-guide.md
# with a repo-scripted updater on a systemd timer.
#
# Model:
#   - `update` reads the public IP (api.ipify.org) and PUTs/creates the name.com A
#     record only when it has changed (idempotent, quiet on no-change).
#   - A root-owned `euler-ddns.timer` runs `update` periodically (like the acme.sh
#     renewal cron). The updater is **infra egress** — like acme.sh, it does NOT go
#     through the Squid proxy (that gate is for the shell / AI / scraper / gh).
#   - Credentials come from the project env file keys/.env (the same name.com token as
#     the DNS-01 challenge); the root timer can read it, so nothing is duplicated.
#
# name.com v4 REST API, HTTP Basic auth (username : API token).
#
# Actions: install [fqdn] | update [fqdn] | status [fqdn] | uninstall | help
#
# Author: Vikas Munshi <vikas.munshi@gmail.com>
# Copyright (c) 2026. All rights reserved.
# Licensed under the MIT License.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
SELF="${PROJECT_ROOT}/scripts/setup/ddns.sh"
ENV_FILE="${PROJECT_ROOT}/keys/.env"          # name.com credentials (read by root)

DEFAULT_FQDN="${EULER_TLS_DOMAIN:-euler.vikasmunshi.com}"
API="https://api.name.com/v4"
IP_SERVICE="${EULER_DDNS_IP_SERVICE:-https://api.ipify.org}"
TTL="${EULER_DDNS_TTL:-300}"

SERVICE_NAME="euler-ddns.service"
TIMER_NAME="euler-ddns.timer"
SERVICE_DEST="/etc/systemd/system/${SERVICE_NAME}"
TIMER_DEST="/etc/systemd/system/${TIMER_NAME}"

# Set by load_creds / split_fqdn.
NAMECOM_USER=""
NAMECOM_TOKEN=""
DOMAIN=""
HOST=""

usage() {
    cat <<USAGE
Usage: $0 [install [fqdn]|update [fqdn]|status [fqdn]|uninstall|help]

  install [fqdn]  Install the euler-ddns systemd timer (root) that periodically
                  updates the A record for <fqdn> (default ${DEFAULT_FQDN}).
  update  [fqdn]  Update the name.com A record now if the public IP changed.
  status  [fqdn]  Show the timer state, the host's public IP, and the live A record.
  uninstall       Remove the timer + service (name.com records left untouched).

  Credentials: NAMEDOTCOM_USERNAME / NAMEDOTCOM_TOKEN in ${ENV_FILE}.
USAGE
}

check_can_sudo() {
    if ! command -v sudo &> /dev/null; then
        echo "Error: sudo is not installed or not found in PATH" >&2
        return 1
    fi
    if ! sudo -v 2>/dev/null; then
        echo "Error: current user does not have sudo privileges" >&2
        return 1
    fi
}

require_systemd() {
    if [ ! -d /run/systemd/system ] || ! command -v systemctl &> /dev/null; then
        echo "Error: systemd is required for the DDNS timer; it is not active here." >&2
        return 1
    fi
}

ensure_deps() {
    if ! command -v jq &> /dev/null; then
        echo "Installing jq..."
        sudo apt-get install -y jq
    fi
}

# Load the name.com username/token from keys/.env (accepting either the NAMEDOTCOM_*
# or the acme.sh Namecom_* spelling). Errors if unset.
load_creds() {
    if [ -f "${ENV_FILE}" ]; then
        set -a
        # shellcheck disable=SC1090
        . "${ENV_FILE}"
        set +a
    fi
    NAMECOM_USER="${Namecom_Username:-${NAMEDOTCOM_USERNAME:-}}"
    NAMECOM_TOKEN="${Namecom_Token:-${NAMEDOTCOM_TOKEN:-}}"
    if [ -z "${NAMECOM_USER}" ] || [ -z "${NAMECOM_TOKEN}" ]; then
        echo "Error: name.com credentials not found in ${ENV_FILE}" \
             "(NAMEDOTCOM_USERNAME / NAMEDOTCOM_TOKEN)" >&2
        return 1
    fi
}

# Split a FQDN into the registered domain (last two labels) and the host prefix.
# e.g. euler.vikasmunshi.com -> DOMAIN=vikasmunshi.com, HOST=euler.
split_fqdn() {
    local fqdn="$1"
    DOMAIN="$(printf '%s' "${fqdn}" | awk -F. '{ if (NF>=2) print $(NF-1)"."$NF; else print $0 }')"
    if [ "${fqdn}" = "${DOMAIN}" ]; then HOST=""; else HOST="${fqdn%.${DOMAIN}}"; fi
}

# Print the host's current public IPv4, or fail.
get_public_ip() {
    local ip
    ip="$(curl -sS --max-time 10 "${IP_SERVICE}" 2>/dev/null || true)"
    [[ "${ip}" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]] || return 1
    printf '%s' "${ip}"
}

# ── update ────────────────────────────────────────────────────────────────────────

do_update() {
    local fqdn="${1:-${DEFAULT_FQDN}}"
    load_creds || return 1
    split_fqdn "${fqdn}"

    local ip
    if ! ip="$(get_public_ip)"; then
        echo "DDNS: could not determine public IP (via ${IP_SERVICE})" >&2
        return 1
    fi

    local records
    if ! records="$(curl -sS -u "${NAMECOM_USER}:${NAMECOM_TOKEN}" --max-time 20 \
            "${API}/domains/${DOMAIN}/records")"; then
        echo "DDNS: name.com records query failed for ${DOMAIN}" >&2
        return 1
    fi

    local id cur
    id="$(printf '%s' "${records}" | jq -r --arg h "${HOST}" \
        'first(.records[]? | select(.host==$h and .type=="A") | .id) // empty')"
    cur="$(printf '%s' "${records}" | jq -r --arg h "${HOST}" \
        'first(.records[]? | select(.host==$h and .type=="A") | .answer) // empty')"

    if [ "${cur}" = "${ip}" ]; then
        echo "DDNS: ${fqdn} already ${ip} (no change)"
        return 0
    fi

    local body
    body="$(jq -nc --arg h "${HOST}" --arg a "${ip}" --argjson t "${TTL}" \
        '{host:$h, type:"A", answer:$a, ttl:$t}')"

    if [ -n "${id}" ]; then
        echo "DDNS: updating ${fqdn} ${cur:-<none>} -> ${ip} (record ${id})"
        curl -sS -u "${NAMECOM_USER}:${NAMECOM_TOKEN}" --max-time 20 -X PUT \
            -H 'Content-Type: application/json' -d "${body}" \
            "${API}/domains/${DOMAIN}/records/${id}" > /dev/null
    else
        echo "DDNS: creating ${fqdn} A ${ip}"
        curl -sS -u "${NAMECOM_USER}:${NAMECOM_TOKEN}" --max-time 20 -X POST \
            -H 'Content-Type: application/json' -d "${body}" \
            "${API}/domains/${DOMAIN}/records" > /dev/null
    fi
    echo "DDNS: ${fqdn} -> ${ip} done"
}

# ── install / uninstall (root timer) ──────────────────────────────────────────────

do_install() {
    local fqdn="${1:-${DEFAULT_FQDN}}"
    check_can_sudo || return 1
    require_systemd || return 1
    ensure_deps
    load_creds || return 1        # fail early if the token is missing

    echo "Installing ${TIMER_NAME} for ${fqdn} (updates every 5 min)..."
    sudo tee "${SERVICE_DEST}" > /dev/null <<EOF
[Unit]
Description=euler dynamic DNS updater (name.com A record for ${fqdn})
Documentation=https://github.com/vikasmunshi/euler/blob/master/docs/tls-guide.md
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=${SELF} update ${fqdn}
EOF
    sudo tee "${TIMER_DEST}" > /dev/null <<EOF
[Unit]
Description=Periodic euler DDNS update

[Timer]
OnBootSec=1min
OnUnitActiveSec=5min
Persistent=true

[Install]
WantedBy=timers.target
EOF
    sudo systemctl daemon-reload
    sudo systemctl enable --now "${TIMER_NAME}"
    echo "Running an initial update..."
    sudo systemctl start "${SERVICE_NAME}" || true
    do_status "${fqdn}"
}

do_uninstall() {
    check_can_sudo || return 1
    if [ -f "${TIMER_DEST}" ]; then
        sudo systemctl disable --now "${TIMER_NAME}" 2>/dev/null || true
        sudo rm -f "${TIMER_DEST}"
    fi
    if [ -f "${SERVICE_DEST}" ]; then
        sudo systemctl disable "${SERVICE_NAME}" 2>/dev/null || true
        sudo rm -f "${SERVICE_DEST}"
    fi
    sudo systemctl daemon-reload
    echo "DDNS uninstall complete (name.com records left untouched)."
}

do_status() {
    local fqdn="${1:-${DEFAULT_FQDN}}"
    echo "DDNS target: ${fqdn}"
    if [ -f "${TIMER_DEST}" ] && command -v systemctl &> /dev/null; then
        echo "${TIMER_NAME}: $(systemctl is-active "${TIMER_NAME}" 2>/dev/null)/$(systemctl is-enabled "${TIMER_NAME}" 2>/dev/null)"
        systemctl list-timers "${TIMER_NAME}" --no-pager 2>/dev/null | sed -n '2p' | sed 's/^/  next: /'
    else
        echo "${TIMER_NAME}: ✗ not installed"
    fi
    local ip
    ip="$(get_public_ip 2>/dev/null || true)"
    echo "Public IP:   ${ip:-unknown}"
    if load_creds 2>/dev/null; then
        split_fqdn "${fqdn}"
        local cur
        cur="$(curl -sS -u "${NAMECOM_USER}:${NAMECOM_TOKEN}" --max-time 15 \
            "${API}/domains/${DOMAIN}/records" 2>/dev/null \
            | jq -r --arg h "${HOST}" 'first(.records[]? | select(.host==$h and .type=="A") | .answer) // "none"' \
            2>/dev/null || true)"
        if [ -n "${ip}" ] && [ "${cur}" = "${ip}" ]; then
            echo "A record:    ${cur} ✓ in sync"
        else
            echo "A record:    ${cur:-unknown} (public IP ${ip:-?})"
        fi
    fi
}

# ── Dispatch ──────────────────────────────────────────────────────────────────────
ACTION="${1:-status}"
case "${ACTION}" in
    install)   do_install "${2:-}" ;;
    update)    do_update "${2:-}" ;;
    status)    do_status "${2:-}" ;;
    uninstall) do_uninstall ;;
    -h | --help | help) usage ;;
    *) echo "Unknown action: ${ACTION}"; usage; exit 1 ;;
esac

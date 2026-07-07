#!/usr/bin/env bash
# Dynamic DNS Updater (name.com A record) — host-scripted, for public edge access
# ================================================================================
#
# Keeps the edge's A record (e.g. euler.vikasmunshi.com) pointed at the host's current
# public IP, so the Caddy edge (scripts/setup/frontend.sh) stays reachable behind a
# changing ISP address. Replaces the "external updater" hand-wave in docs/tls-guide.md
# with a repo-scripted updater on a systemd timer.
#
# Model (DD-4 — runs as the non-root euler-ddns user):
#   - `update` reads the public IP (api.ipify.org) and PUTs/creates the name.com A
#     record only when it has changed (idempotent, quiet on no-change).
#   - The updater is deployed to /usr/local/bin/euler-ddns and run by a root-owned
#     `euler-ddns.timer` as the dedicated `euler-ddns` user. It is **infra egress** —
#     like acme.sh, it does NOT go through the Squid proxy.
#   - Config is the scoped /etc/euler/ddns.env (root:euler-ddns 0640): just the FQDN
#     (EULER_TLS_DOMAIN) + the name.com token, deployed by the installer from keys/.env
#     (the authoring source). euler-ddns never reads the full keys/.env.
#
# name.com v4 REST API, HTTP Basic auth (username : API token).
#
# Actions: install | update | status | uninstall | help
#
# Author: Vikas Munshi <vikas.munshi@gmail.com>
# Copyright (c) 2026. All rights reserved.
# Licensed under the MIT License.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
SELF="${SCRIPT_DIR}/ddns.sh"                    # this script in the repo (for deploy)
ENV_FILE="${PROJECT_ROOT}/keys/.env"            # authoring source (operator-readable)

SYS_DIR="/etc/euler"
DDNS_ENV="${SYS_DIR}/ddns.env"                  # scoped runtime config (root:euler-ddns 0640)
DDNS_BIN="/usr/local/bin/euler-ddns"            # deployed updater (euler-ddns runs this)
DDNS_USER="euler-ddns"
DDNS_GROUP="euler-ddns"

API="https://api.name.com/v4"
IP_SERVICE="${EULER_DDNS_IP_SERVICE:-https://api.ipify.org}"
TTL="${EULER_DDNS_TTL:-300}"

SERVICE_NAME="euler-ddns.service"
TIMER_NAME="euler-ddns.timer"
SERVICE_DEST="/etc/systemd/system/${SERVICE_NAME}"
TIMER_DEST="/etc/systemd/system/${TIMER_NAME}"

# Set by load_config / split_fqdn.
FQDN=""              # full deployment FQDN (EULER_TLS_DOMAIN)
NAMECOM_USER=""
NAMECOM_TOKEN=""
DOMAIN=""            # registered domain (last two labels of FQDN)
HOST=""              # subdomain prefix

usage() {
    cat <<USAGE
Usage: $0 [install|update|status|uninstall|help]

  install    Install the euler-ddns systemd timer (root) that periodically updates
             the A record for the FQDN from keys/.env.
  update     Update the name.com A record now if the public IP changed.
  status     Show the timer state, the host's public IP, and the live A record.
  uninstall  Remove the timer + service (name.com records left untouched).

  Authoring config in keys/.env: EULER_TLS_DOMAIN (the FQDN) and NAMEDOTCOM_USERNAME /
  NAMEDOTCOM_TOKEN. install deploys a scoped copy to /etc/euler/ddns.env for euler-ddns;
  commands fail if the FQDN is unset.
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

# Source the config and resolve the FQDN + name.com creds. Prefers the deployed scoped
# /etc/euler/ddns.env (readable by euler-ddns / root); falls back to the repo keys/.env
# (operator). Fails if the FQDN is set in neither.
load_config() {
    local src=""
    if [ -r "${DDNS_ENV}" ]; then
        src="${DDNS_ENV}"
    elif [ -r "${ENV_FILE}" ]; then
        src="${ENV_FILE}"
    fi
    if [ -n "${src}" ]; then
        set -a
        # shellcheck disable=SC1090
        . "${src}"
        set +a
    fi
    FQDN="${EULER_TLS_DOMAIN:-}"
    NAMECOM_USER="${Namecom_Username:-${NAMEDOTCOM_USERNAME:-}}"
    NAMECOM_TOKEN="${Namecom_Token:-${NAMEDOTCOM_TOKEN:-}}"
    if [ -z "${FQDN}" ]; then
        echo "Error: EULER_TLS_DOMAIN not set in ${DDNS_ENV} or ${ENV_FILE}" >&2
        return 1
    fi
}

# Assert the name.com credentials were found (needed for update + the status A-lookup).
require_creds() {
    if [ -z "${NAMECOM_USER}" ] || [ -z "${NAMECOM_TOKEN}" ]; then
        echo "Error: name.com credentials not found (NAMEDOTCOM_USERNAME / NAMEDOTCOM_TOKEN)" >&2
        return 1
    fi
}

# Create the dedicated euler-ddns user (own group, nologin) — DD-4.
ensure_ddns_user() {
    if ! getent group "${DDNS_GROUP}" > /dev/null; then
        sudo groupadd --system "${DDNS_GROUP}"
    fi
    if ! getent passwd "${DDNS_USER}" > /dev/null; then
        echo "Creating system user ${DDNS_USER}..."
        sudo useradd --system --no-create-home --shell /usr/sbin/nologin \
            -g "${DDNS_GROUP}" "${DDNS_USER}"
    fi
}

# Deploy the scoped runtime config euler-ddns reads (FQDN + name.com creds only).
deploy_ddns_env() {
    sudo mkdir -p "${SYS_DIR}"
    sudo tee "${DDNS_ENV}" > /dev/null <<EOF
# GENERATED by scripts/setup/ddns.sh — scoped runtime config for euler-ddns (DD-4).
# Authoring source: keys/.env.
EULER_TLS_DOMAIN=${FQDN}
NAMEDOTCOM_USERNAME=${NAMECOM_USER}
NAMEDOTCOM_TOKEN=${NAMECOM_TOKEN}
EOF
    sudo chown root:"${DDNS_GROUP}" "${DDNS_ENV}"
    sudo chmod 0640 "${DDNS_ENV}"
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
    load_config || return 1
    require_creds || return 1
    split_fqdn "${FQDN}"

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
        echo "DDNS: ${FQDN} already ${ip} (no change)"
        return 0
    fi

    local body
    body="$(jq -nc --arg h "${HOST}" --arg a "${ip}" --argjson t "${TTL}" \
        '{host:$h, type:"A", answer:$a, ttl:$t}')"

    if [ -n "${id}" ]; then
        echo "DDNS: updating ${FQDN} ${cur:-<none>} -> ${ip} (record ${id})"
        curl -sS -u "${NAMECOM_USER}:${NAMECOM_TOKEN}" --max-time 20 -X PUT \
            -H 'Content-Type: application/json' -d "${body}" \
            "${API}/domains/${DOMAIN}/records/${id}" > /dev/null
    else
        echo "DDNS: creating ${FQDN} A ${ip}"
        curl -sS -u "${NAMECOM_USER}:${NAMECOM_TOKEN}" --max-time 20 -X POST \
            -H 'Content-Type: application/json' -d "${body}" \
            "${API}/domains/${DOMAIN}/records" > /dev/null
    fi
    echo "DDNS: ${FQDN} -> ${ip} done"
}

# ── install / uninstall (root timer) ──────────────────────────────────────────────

do_install() {
    check_can_sudo || return 1
    require_systemd || return 1
    load_config || return 1
    require_creds || return 1      # fail early if the token is missing
    ensure_deps
    ensure_ddns_user
    deploy_ddns_env
    echo "Deploying updater to ${DDNS_BIN}..."
    sudo install -m 0755 "${SELF}" "${DDNS_BIN}"

    echo "Installing ${TIMER_NAME} for ${FQDN} (every 5 min, as ${DDNS_USER})..."
    sudo tee "${SERVICE_DEST}" > /dev/null <<EOF
[Unit]
Description=euler dynamic DNS updater (name.com A record for ${FQDN})
Documentation=https://github.com/vikasmunshi/euler/blob/master/docs/tls-guide.md
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=${DDNS_USER}
Group=${DDNS_GROUP}
ExecStart=${DDNS_BIN} update
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
    do_status
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
    sudo rm -f "${DDNS_BIN}"

    local reply
    read -r -p "Remove ${DDNS_ENV} and the ${DDNS_USER} user? [y/N] " reply
    if [[ "${reply}" =~ ^[Yy]$ ]]; then
        sudo rm -f "${DDNS_ENV}"
        if getent passwd "${DDNS_USER}" > /dev/null; then sudo userdel "${DDNS_USER}" 2>/dev/null || true; fi
        if getent group "${DDNS_GROUP}" > /dev/null; then sudo groupdel "${DDNS_GROUP}" 2>/dev/null || true; fi
    fi
    echo "DDNS uninstall complete (name.com records left untouched)."
}

do_status() {
    load_config || return 1
    echo "DDNS target: ${FQDN}"
    if [ -f "${TIMER_DEST}" ] && command -v systemctl &> /dev/null; then
        echo "${TIMER_NAME}: $(systemctl is-active "${TIMER_NAME}" 2>/dev/null)/$(systemctl is-enabled "${TIMER_NAME}" 2>/dev/null)"
        systemctl list-timers "${TIMER_NAME}" --no-pager 2>/dev/null | sed -n '2p' | sed 's/^/  next: /'
    else
        echo "${TIMER_NAME}: ✗ not installed"
    fi
    local ip
    ip="$(get_public_ip 2>/dev/null || true)"
    echo "Public IP:   ${ip:-unknown}"
    if require_creds 2>/dev/null; then
        split_fqdn "${FQDN}"
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
    install)   do_install ;;
    update)    do_update ;;
    status)    do_status ;;
    uninstall) do_uninstall ;;
    -h | --help | help) usage ;;
    *) echo "Unknown action: ${ACTION}"; usage; exit 1 ;;
esac

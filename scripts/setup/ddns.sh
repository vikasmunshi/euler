#!/usr/bin/env bash
# Dynamic DNS Updater (name.com A record) — host-scripted, for public edge access
# ================================================================================
#
# Keeps the edge's A record (e.g. euler.vikasmunshi.com) pointed at the host's current
# public IP, so the Caddy edge (scripts/setup/frontend.sh) stays reachable behind a
# changing ISP address. Replaces the "external updater" hand-wave in docs/web-server-guide.md
# with a repo-scripted updater on a systemd timer.
#
# This is the INSTALLER half of the kit. The updater it deploys is a separate file,
# scripts/setup/euler-ddns.sh, which holds everything that talks to name.com —
# mirroring smtp.sh / euler-smtp.py. The two halves are split because they have
# different privileges and different dependencies: this one runs from the checkout as
# the operator and reads the (possibly vault-encrypted) authoring env; the updater runs
# as a locked-down uid from /usr/local/bin and reads only the scoped plaintext copy.
# Deploying THIS file as the updater is what previously carried the installer's sibling
# helpers to a directory without them, killing the timer silently.
#
# Model (the updater runs as the non-root euler-ddns user):
#   - `update` reads the public IP (api.ipify.org) and PUTs/creates the name.com A
#     record only when it has changed (idempotent, quiet on no-change).
#   - The updater is deployed to /usr/local/bin/euler-ddns and run by a root-owned
#     `euler-ddns.timer` as the dedicated `euler-ddns` user. It is **infra egress** —
#     like acme.sh, it does NOT go through the Squid proxy.
#   - Config is the scoped /etc/euler/ddns.env (root:euler-ddns 0640): just the FQDN
#     (EULER_TLS_DOMAIN) + the name.com token, deployed by the installer from ~/.euler/env
#     (the authoring source). euler-ddns never reads the full ~/.euler/env.
#
# Actions: deploy | update | status | remove | help
#
# Author: Vikas Munshi <vikas.munshi@gmail.com>
# Copyright (c) 2026. All rights reserved.
# Licensed under the MIT License.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
UPDATER_SRC="${SCRIPT_DIR}/euler-ddns.sh"       # the runtime updater this kit deploys
# The authoring env (~/.euler/env, possibly vault-encrypted): ENV_FILE +
# load_authoring_env, shared so every kit reads it one way. Unconditional: this file is
# the installer and never leaves the checkout, so its helpers are always beside it.
# shellcheck source=scripts/setup/authoring_env.sh
. "${SCRIPT_DIR}/authoring_env.sh"

SYS_DIR="/etc/euler"
DDNS_ENV="${SYS_DIR}/ddns.env"                  # scoped runtime config (root:euler-ddns 0640)
DDNS_BIN="/usr/local/bin/euler-ddns"            # deployed updater (euler-ddns runs this)
DDNS_USER="euler-ddns"
DDNS_GROUP="euler-ddns"

SERVICE_NAME="euler-ddns.service"
TIMER_NAME="euler-ddns.timer"
SERVICE_DEST="/etc/systemd/system/${SERVICE_NAME}"
TIMER_DEST="/etc/systemd/system/${TIMER_NAME}"

# Set by load_config.
FQDN=""              # full deployment FQDN (EULER_TLS_DOMAIN)
NAMECOM_USER=""
NAMECOM_TOKEN=""

usage() {
    cat <<USAGE
Usage: $0 [deploy|update|status|remove|help]

  deploy     Install the euler-ddns systemd timer (root) that periodically updates
             the A record for the FQDN from ~/.euler/env. Idempotent — it is also
             its own upgrade path.
  update     Update the name.com A record now if the public IP changed.
  status     Show the timer state, the host's public IP, and the live A record.
  remove     Remove the timer + service (name.com records left untouched).

  Authoring config in ~/.euler/env: EULER_TLS_DOMAIN (the FQDN) and NAMEDOTCOM_USERNAME /
  NAMEDOTCOM_TOKEN. deploy installs a scoped copy to /etc/euler/ddns.env for euler-ddns;
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
# /etc/euler/ddns.env (readable by euler-ddns / root); falls back to the repo ~/.euler/env
# (operator). Fails if the FQDN is set in neither.
#
# The precedence resolves itself by permission: ddns.env is root:euler-ddns 0640, so the
# operator running an install cannot read it and lands on the authoring env, while root
# re-reads the scoped copy it already deployed.
#
# The two sources take different paths on purpose: ddns.env is generated by
# deploy_ddns_env and is therefore ALWAYS plaintext, while only ~/.euler/env can be vault
# ciphertext and need the reader. `set -a` in both branches is what lets do_update simply
# exec the updater — the config is already in the environment.
load_config() {
    if [ -r "${DDNS_ENV}" ]; then
        set -a
        # shellcheck disable=SC1090
        . "${DDNS_ENV}"
        set +a
    elif [ -r "${ENV_FILE}" ]; then
        load_authoring_env "${ENV_FILE}" || return 1
    fi
    FQDN="${EULER_TLS_DOMAIN:-}"
    NAMECOM_USER="${Namecom_Username:-${NAMEDOTCOM_USERNAME:-}}"
    NAMECOM_TOKEN="${Namecom_Token:-${NAMEDOTCOM_TOKEN:-}}"
    if [ -z "${FQDN}" ]; then
        echo "Error: EULER_TLS_DOMAIN not set in ${DDNS_ENV} or ${ENV_FILE}" >&2
        return 1
    fi
}

# Assert the name.com credentials were found (needed for update + deploying ddns.env).
require_creds() {
    if [ -z "${NAMECOM_USER}" ] || [ -z "${NAMECOM_TOKEN}" ]; then
        echo "Error: name.com credentials not found (NAMEDOTCOM_USERNAME / NAMEDOTCOM_TOKEN)" >&2
        return 1
    fi
}

# Create the dedicated euler-ddns user (own group, nologin).
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
# GENERATED by scripts/setup/ddns.sh — scoped runtime config for euler-ddns.
# Authoring source: ~/.euler/env.
EULER_TLS_DOMAIN=${FQDN}
NAMEDOTCOM_USERNAME=${NAMECOM_USER}
NAMEDOTCOM_TOKEN=${NAMECOM_TOKEN}
EOF
    sudo chown root:"${DDNS_GROUP}" "${DDNS_ENV}"
    sudo chmod 0640 "${DDNS_ENV}"
}

# ── update ────────────────────────────────────────────────────────────────────────

# Run the updater from the REPO, not ${DDNS_BIN}: an operator running this wants the
# current source exercised, not yesterday's deployed copy. load_config exports the
# config (`set -a`), and the operator cannot read the root-owned scoped ddns.env, so
# the updater picks up the authoring values from the environment — the vault decrypt
# happens here, in the one place that is allowed to do it.
do_update() {
    load_config || return 1
    require_creds || return 1
    "${UPDATER_SRC}" update
}

# ── deploy / remove (root timer) ──────────────────────────────────────────────────

do_deploy() {
    check_can_sudo || return 1
    require_systemd || return 1
    load_config || return 1
    require_creds || return 1      # fail early if the token is missing
    ensure_deps
    ensure_ddns_user
    deploy_ddns_env
    echo "Deploying updater to ${DDNS_BIN}..."
    sudo install -m 0755 "${UPDATER_SRC}" "${DDNS_BIN}"

    echo "Installing ${TIMER_NAME} for ${FQDN} (every 5 min, as ${DDNS_USER})..."
    sudo tee "${SERVICE_DEST}" > /dev/null <<EOF
[Unit]
Description=euler dynamic DNS updater (name.com A record for ${FQDN})
Documentation=https://github.com/vikasmunshi/euler/blob/master/docs/web-server-guide.md
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

    # The initial update is the ONLY check that the deployed updater actually runs as
    # euler-ddns — do_status below answers from the operator's checkout and stays green
    # even when ${DDNS_BIN} is broken, so a failure swallowed here is a timer that has
    # been failing every 5 minutes in silence.
    echo "Running an initial update..."
    if ! sudo systemctl start "${SERVICE_NAME}"; then
        echo "Error: the initial update failed — the timer is deployed but the updater at" >&2
        echo "       ${DDNS_BIN} is not working, so the A record will go stale." >&2
        echo "       Diagnose with: journalctl -xeu ${SERVICE_NAME}" >&2
        do_status || true
        return 1
    fi
    do_status
}

do_remove() {
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
    # The public IP + live A record: the updater owns every name.com call, so status
    # asks it rather than keeping a second copy of the query. Best-effort — a name.com
    # hiccup must not fail a status report.
    "${UPDATER_SRC}" show || true
}

# ── Dispatch ──────────────────────────────────────────────────────────────────────
ACTION="${1:-status}"
case "${ACTION}" in
    deploy)    do_deploy ;;
    update)    do_update ;;
    status)    do_status ;;
    remove)    do_remove ;;
    -h | --help | help) usage ;;
    *) echo "Unknown action: ${ACTION}"; usage; exit 1 ;;
esac

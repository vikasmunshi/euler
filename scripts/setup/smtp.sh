#!/usr/bin/env bash
# Loopback SMTP relay (euler-smtp)
# ================================================================================
#
# Installs / uninstalls the small loopback submission relay through which the app
# tier (first euler-auth: OTP + invite mail) sends email — so no app service needs
# a direct-internet exception or the Gmail credentials. Sibling to frontend.sh /
# egress.sh / ddns.sh / firewall.sh; see docs/web-server-guide.md § Egress.
#
# Model:
#   - The relay (scripts/setup/euler-smtp.py, deployed to /usr/local/bin/euler-smtp)
#     listens on loopback 127.0.0.1:8025 and relays upstream to Gmail submission
#     (smtp.gmail.com:587, STARTTLS + app password). Stdlib-only, system python3.
#   - It runs as the dedicated `euler-smtp` user (own group, outside euler-web) and
#     is the sole holder of the Gmail creds and — per firewall.sh — the sole
#     euler-* uid permitted tcp :587.
#   - Clients (euler-auth) submit over plain loopback SMTP, no credentials; the
#     envelope sender is always forced to SMTP_ADDRESS.
#   - Config is the scoped /etc/euler/smtp.env (root:euler-smtp 0640), deployed by
#     the installer from ~/.euler/env (the authoring source: SMTP_ADDRESS /
#     SMTP_APP_PASSWORD). euler-smtp never reads the full ~/.euler/env.
#
#   /etc/euler/smtp.env                    root:euler-smtp 0640  (generated here)
#   /usr/local/bin/euler-smtp              root:root 0755        (deployed relay)
#   /etc/systemd/system/euler-smtp.service (root-owned, boot-enabled)
#
# Because the unit lives in root's systemd and runs as a locked-down user, lifecycle
# (start/stop/restart) requires sudo.
#
# Actions: install | uninstall | upgrade | status | test | help
#
# Author: Vikas Munshi <vikas.munshi@gmail.com>
# Copyright (c) 2026. All rights reserved.
# Licensed under the MIT License.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
RELAY_SRC="${SCRIPT_DIR}/euler-smtp.py"         # relay source in the repo (for deploy)
# The authoring env (~/.euler/env, possibly vault-encrypted): ENV_FILE +
# load_authoring_env, shared so every kit reads it one way.
# shellcheck source=scripts/setup/authoring_env.sh
. "${SCRIPT_DIR}/authoring_env.sh"

SYS_DIR="/etc/euler"
SMTP_ENV="${SYS_DIR}/smtp.env"                  # scoped runtime config (root:euler-smtp 0640)
RELAY_BIN="/usr/local/bin/euler-smtp"           # deployed relay (euler-smtp runs this)
SMTP_USER="euler-smtp"
SMTP_GROUP="euler-smtp"

# The loopback listener euler-auth submits to (EULER_SMTP_RELAY in auth.env).
LISTEN_ADDR="${EULER_SMTP_LISTEN:-127.0.0.1:8025}"
UPSTREAM_HOST="smtp.gmail.com"
UPSTREAM_PORT="587"

SERVICE_NAME="euler-smtp.service"
SERVICE_DEST="/etc/systemd/system/${SERVICE_NAME}"

# Set by load_config.
SMTP_ADDRESS=""
SMTP_APP_PASSWORD=""

usage() {
    cat <<USAGE
Usage: $0 [install|uninstall|upgrade|status|test|help]

  install    Create the euler-smtp user, deploy the relay + scoped smtp.env, and
             install the root-owned, boot-enabled euler-smtp.service.
  uninstall  Remove the service + relay (prompts before removing smtp.env + user).
  upgrade    Redeploy the relay, regenerate smtp.env + unit, restart.
  status     Show the unit state and probe the loopback listener (EHLO).
  test       Send a real test mail to SMTP_ADDRESS through the relay.

  Authoring config in ~/.euler/env: SMTP_ADDRESS + SMTP_APP_PASSWORD (Gmail app
  password). install deploys a scoped copy to ${SMTP_ENV} for ${SMTP_USER}.
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
        echo "Error: systemd is required for the relay service; it is not active here." >&2
        return 1
    fi
}

# Source the config and resolve the Gmail creds. Prefers the deployed scoped
# /etc/euler/smtp.env (readable by root/euler-smtp); falls back to the repo ~/.euler/env
# (operator). Fails if the creds are set in neither.
load_config() {
    local src=""
    if [ -r "${SMTP_ENV}" ]; then
        src="${SMTP_ENV}"
    elif [ -r "${ENV_FILE}" ]; then
        src="${ENV_FILE}"
    fi
    if [ -n "${src}" ]; then
        load_authoring_env "${src}" || return 1
    fi
    if [ -z "${SMTP_ADDRESS:-}" ] || [ -z "${SMTP_APP_PASSWORD:-}" ]; then
        echo "Error: SMTP_ADDRESS / SMTP_APP_PASSWORD not set in ${SMTP_ENV} or ${ENV_FILE}" >&2
        return 1
    fi
}

# Create the dedicated euler-smtp user (own group, nologin, outside euler-web).
ensure_smtp_user() {
    if ! getent group "${SMTP_GROUP}" > /dev/null; then
        sudo groupadd --system "${SMTP_GROUP}"
    fi
    if ! getent passwd "${SMTP_USER}" > /dev/null; then
        echo "Creating system user ${SMTP_USER}..."
        sudo useradd --system --no-create-home --shell /usr/sbin/nologin \
            -g "${SMTP_GROUP}" "${SMTP_USER}"
    fi
}

# Deploy the scoped runtime config euler-smtp reads (Gmail creds + listener only).
deploy_smtp_env() {
    sudo mkdir -p "${SYS_DIR}"
    sudo tee "${SMTP_ENV}" > /dev/null <<EOF
# GENERATED by scripts/setup/smtp.sh — scoped runtime config for euler-smtp.
# Authoring source: ~/.euler/env. Read ONLY by the relay — no app service sees these.
EULER_SMTP_LISTEN=${LISTEN_ADDR}
SMTP_HOST=${UPSTREAM_HOST}
SMTP_PORT=${UPSTREAM_PORT}
SMTP_ADDRESS=${SMTP_ADDRESS}
SMTP_APP_PASSWORD=${SMTP_APP_PASSWORD}
EOF
    sudo chown root:"${SMTP_GROUP}" "${SMTP_ENV}"
    sudo chmod 0640 "${SMTP_ENV}"
}

# ── install / uninstall (root-owned unit) ─────────────────────────────────────────

do_install() {
    check_can_sudo || return 1
    require_systemd || return 1
    load_config || return 1
    ensure_smtp_user
    deploy_smtp_env
    echo "Deploying relay to ${RELAY_BIN}..."
    sudo install -m 0755 "${RELAY_SRC}" "${RELAY_BIN}"

    echo "Installing ${SERVICE_NAME} (loopback ${LISTEN_ADDR} -> ${UPSTREAM_HOST}:${UPSTREAM_PORT}, as ${SMTP_USER})..."
    sudo tee "${SERVICE_DEST}" > /dev/null <<EOF
[Unit]
Description=euler loopback SMTP submission relay
Documentation=https://github.com/vikasmunshi/euler/blob/master/docs/web-server-guide.md
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${SMTP_USER}
Group=${SMTP_GROUP}
EnvironmentFile=${SMTP_ENV}
ExecStart=/usr/bin/python3 ${RELAY_BIN}
Restart=on-failure
RestartSec=5s

# Hardening — loopback listener, upstream :587 only (enforced by firewall.sh).
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
PrivateDevices=true
RestrictAddressFamilies=AF_INET AF_INET6
CapabilityBoundingSet=
LockPersonality=true
MemoryDenyWriteExecute=true
RestrictRealtime=true
SystemCallArchitectures=native

[Install]
WantedBy=multi-user.target
EOF
    sudo systemctl daemon-reload
    sudo systemctl enable --now "${SERVICE_NAME}"
    sudo systemctl restart "${SERVICE_NAME}"

    # The relay uid is part of the nftables egress ruleset — regenerate if installed.
    if [ -f /etc/systemd/system/euler-firewall.service ]; then
        echo "Reloading the egress firewall to include ${SMTP_USER}..."
        "${SCRIPT_DIR}/firewall.sh" reload
    fi
    do_status
}

do_uninstall() {
    check_can_sudo || return 1
    if [ -f "${SERVICE_DEST}" ]; then
        sudo systemctl disable --now "${SERVICE_NAME}" 2>/dev/null || true
        sudo rm -f "${SERVICE_DEST}"
        sudo systemctl daemon-reload
    fi
    sudo rm -f "${RELAY_BIN}"

    local reply
    read -r -p "Remove ${SMTP_ENV} (Gmail creds) and the ${SMTP_USER} user? [y/N] " reply
    if [[ "${reply}" =~ ^[Yy]$ ]]; then
        sudo rm -f "${SMTP_ENV}"
        if getent passwd "${SMTP_USER}" > /dev/null; then sudo userdel "${SMTP_USER}" 2>/dev/null || true; fi
        if getent group "${SMTP_GROUP}" > /dev/null; then sudo groupdel "${SMTP_GROUP}" 2>/dev/null || true; fi
    fi
    echo "SMTP relay uninstall complete."
}

# ── status / test ─────────────────────────────────────────────────────────────────

# Probe the loopback listener: connect, expect 220, EHLO, QUIT.
probe_listener() {
    python3 - "${LISTEN_ADDR}" <<'PY'
import smtplib
import sys

host, _, port = sys.argv[1].rpartition(':')
try:
    with smtplib.SMTP(host, int(port), timeout=5) as smtp:
        code, msg = smtp.ehlo()
        ok = code == 250
        print(f"listener:    {'✓' if ok else '✗'} {host}:{port} EHLO -> {code} {msg.decode().splitlines()[0]}")
        sys.exit(0 if ok else 1)
except OSError as exc:
    print(f"listener:    ✗ {host}:{port} unreachable ({exc})")
    sys.exit(1)
PY
}

do_status() {
    echo "Relay:       ${LISTEN_ADDR} -> ${UPSTREAM_HOST}:${UPSTREAM_PORT} (as ${SMTP_USER})"
    if [ -f "${SERVICE_DEST}" ] && command -v systemctl &> /dev/null; then
        echo "${SERVICE_NAME}: $(systemctl is-active "${SERVICE_NAME}" 2>/dev/null)/$(systemctl is-enabled "${SERVICE_NAME}" 2>/dev/null)"
    else
        echo "${SERVICE_NAME}: ✗ not installed"
    fi
    probe_listener || true
}

# Send a real test mail (to SMTP_ADDRESS itself) through the relay.
do_test() {
    load_config || return 1
    echo "Sending test mail to ${SMTP_ADDRESS} via ${LISTEN_ADDR}..."
    python3 - "${LISTEN_ADDR}" "${SMTP_ADDRESS}" <<'PY'
import smtplib
import sys
from email.message import EmailMessage

listen, rcpt = sys.argv[1], sys.argv[2]
host, _, port = listen.rpartition(':')
msg = EmailMessage()
msg['From'] = rcpt
msg['To'] = rcpt
msg['Subject'] = 'euler-smtp relay test'
msg.set_content('Test mail from the euler-smtp loopback relay (scripts/setup/smtp.sh test).')
with smtplib.SMTP(host, int(port), timeout=60) as smtp:
    smtp.send_message(msg)
print('✓ relay accepted the message — check the inbox.')
PY
}

# ── Dispatch ──────────────────────────────────────────────────────────────────────
ACTION="${1:-status}"
case "${ACTION}" in
    install)   do_install ;;
    upgrade)   do_install ;;
    uninstall) do_uninstall ;;
    status)    do_status ;;
    test)      do_test ;;
    -h | --help | help) usage ;;
    *) echo "Unknown action: ${ACTION}"; usage; exit 1 ;;
esac

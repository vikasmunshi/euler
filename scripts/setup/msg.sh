#!/usr/bin/env bash
# Message spool service (euler-msg)
# ================================================================================
#
# Deploys / removes the message spool — the user↔staff messaging tier described in
# docs/web-server-guide.md § Messaging. Sibling to auth.sh / smtp.sh / user.sh.
#
# Model:
#   - The service (python -m solver.web.msg) runs as the dedicated `euler-msg` user
#     from the shared root-owned /opt/euler venv, which **auth.sh owns** — this kit
#     never builds or reinstalls it, it only restarts the service against it.
#   - Two unix sockets, no network at all:
#       /run/euler/msg.sock       0660 euler-msg:euler-web — the per-user services and
#                                 their PTY children; identity is SO_PEERCRED.
#       /run/euler-msg/admin.sock 0600 euler-msg-private   — the operator's terminal,
#                                 via sudo. Its own RuntimeDirectory rather than
#                                 /run/euler-adm, which is euler-auth-private.
#   - The unit is RestrictAddressFamilies=AF_UNIX: this process cannot open a network
#     socket at all. That is what dropping the mail path bought, so do not add
#     AF_INET here without reading § Messaging — No mail first.
#   - It is NOT routed by Caddy. The per-user service is its only web-facing consumer,
#     so no Caddyfile change belongs with this kit.
#   - Authorization reads /etc/euler/authorizations.json (world-readable, root-write),
#     so the spool needs no contact with the auth service and holds no roster of its own.
#
#   /etc/euler/msg.env                     root:euler-msg 0640  (generated here)
#   /var/lib/euler-msg                     euler-msg:euler-msg 0700 (the spool)
#   /etc/systemd/system/euler-msg.service  (root-owned, boot-enabled)
#
# Because the unit lives in root's systemd and runs as a locked-down user, lifecycle
# (start/stop/restart) requires sudo.
#
# Actions: deploy | remove | upgrade | redeploy | status | help
#
# Author: Vikas Munshi <vikas.munshi@gmail.com>
# Copyright (c) 2026. All rights reserved.
# Licensed under the MIT License.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# The system venv — OPT_DIR / VENV_DIR / VENV_PY / PYTHON, shared with the other app
# kits. This kit reads it; auth.sh is the one that builds it.
# shellcheck source=scripts/setup/venv.sh
. "${SCRIPT_DIR}/venv.sh"

SYS_DIR="/etc/euler"
MSG_ENV="${SYS_DIR}/msg.env"                    # scoped runtime config (root:euler-msg 0640)
AUTHZ_FILE="${SYS_DIR}/authorizations.json"     # the policy the spool reads (auth.sh owns it)
STATE_DIR="/var/lib/euler-msg"                  # euler-msg-only spool
MSG_USER="euler-msg"
MSG_GROUP="euler-msg"
WEB_GROUP="euler-web"

MSG_SOCKET="/run/euler/msg.sock"
ADMIN_RUNTIME_DIR="/run/euler-msg"
ADMIN_SOCKET="${ADMIN_RUNTIME_DIR}/admin.sock"
USER_SOCKET_DIR="/run/euler"

SERVICE_NAME="euler-msg.service"
SERVICE_DEST="/etc/systemd/system/${SERVICE_NAME}"

# Set by resolve_token.
ADMIN_TOKEN=""

usage() {
    cat <<USAGE
Usage: $0 [deploy|remove|upgrade|redeploy|status|help]

  deploy     Create the euler-msg user, /etc/euler/msg.env (with a generated
             root-only EULER_MSG_ADMIN_TOKEN) and ${STATE_DIR}, and install the
             root-owned, boot-enabled ${SERVICE_NAME}. Idempotent.
  upgrade    Alias of deploy — the deploy path is already the re-assert path
             (it regenerates the env file and re-lays the unit).
  redeploy   Fast path: restart the service against the current /opt/euler venv
             (auth.sh redeploy is what refreshes that venv).
  remove     Remove the service (prompts before deleting the spool and the identity).
  status     Report the unit, the identity, the config, the spool, and probe /healthz.

  Needs the shared venv (make deploy-auth) and the policy file it reads. This kit
  never touches ${VENV_DIR} itself.
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
        echo "Error: systemd is required for the message service; it is not active here." >&2
        return 1
    fi
}

require_venv() {
    if [ ! -x "${VENV_PY}" ]; then
        echo "Error: ${VENV_DIR} is not deployed — run 'make deploy-auth' first (it owns the venv)." >&2
        return 1
    fi
    if ! sudo "${VENV_PY}" -P -c 'import solver.web.msg' 2>/dev/null; then
        echo "Error: solver.web.msg is not importable from ${VENV_DIR}." >&2
        echo "       Run 'make redeploy-auth' to reinstall this checkout into the venv." >&2
        return 1
    fi
}

# The admin-plane secret. Kept ONLY in the root-readable msg.env — never in the
# operator's ~/.euler/env, for the same reason the auth token is not: the operator's uid
# is the most exposed on the host, and a token readable there would let anything running
# as them reach the admin plane below sudo.
resolve_token() {
    ADMIN_TOKEN="$(sudo grep -s '^EULER_MSG_ADMIN_TOKEN=' "${MSG_ENV}" 2>/dev/null | head -1 | cut -d= -f2- || true)"
    if [ -z "${ADMIN_TOKEN}" ]; then
        echo "Generating EULER_MSG_ADMIN_TOKEN (kept only in root-readable ${MSG_ENV})..."
        ADMIN_TOKEN="$(${PYTHON} -c 'import secrets; print(secrets.token_hex(32))')"
    fi
}

# The dedicated euler-msg user. In euler-web so it can (a) connect to the per-user
# instance sockets for the delivery nudge and (b) chgrp its own public socket to that
# group at bind time.
ensure_msg_user() {
    if ! getent group "${MSG_GROUP}" > /dev/null; then
        sudo groupadd --system "${MSG_GROUP}"
    fi
    if ! getent group "${WEB_GROUP}" > /dev/null; then
        sudo groupadd --system "${WEB_GROUP}"
    fi
    if ! getent passwd "${MSG_USER}" > /dev/null; then
        echo "Creating system user ${MSG_USER}..."
        sudo useradd --system --no-create-home --shell /usr/sbin/nologin \
            -g "${MSG_GROUP}" -G "${WEB_GROUP}" "${MSG_USER}"
    else
        sudo usermod -a -G "${WEB_GROUP}" "${MSG_USER}"
    fi
}

# Deploy the scoped runtime config euler-msg reads — never the full ~/.euler/env.
# There is deliberately no mail or base-URL setting here: the spool sends no e-mail
# and renders no links.
deploy_msg_env() {
    sudo mkdir -p "${SYS_DIR}"
    sudo tee "${MSG_ENV}" > /dev/null <<EOF
# GENERATED by scripts/setup/msg.sh — scoped runtime config for euler-msg.
# No mail, no base URL, no secrets beyond this plane's own token: the spool speaks
# only over unix sockets (docs/web-server-guide.md § Messaging).
EULER_MSG_ADMIN_TOKEN=${ADMIN_TOKEN}
EULER_MSG_STATE_DIR=${STATE_DIR}
EULER_MSG_SOCKET=${MSG_SOCKET}
EULER_MSG_ADMIN_SOCKET=${ADMIN_SOCKET}
EULER_WEB_GROUP=${WEB_GROUP}
EULER_USER_SOCKET_DIR=${USER_SOCKET_DIR}
EOF
    sudo chown root:"${MSG_GROUP}" "${MSG_ENV}"
    sudo chmod 0640 "${MSG_ENV}"
}

# The euler-msg-only spool dir. The unit's StateDirectory= re-asserts this.
deploy_state_dir() {
    sudo mkdir -p "${STATE_DIR}"
    sudo chown "${MSG_USER}:${MSG_GROUP}" "${STATE_DIR}"
    sudo chmod 0700 "${STATE_DIR}"
}

deploy_unit() {
    echo "Installing ${SERVICE_NAME} (as ${MSG_USER}, unix sockets only)..."
    sudo tee "${SERVICE_DEST}" > /dev/null <<EOF
[Unit]
Description=euler message spool (user<->staff threads)
Documentation=https://github.com/vikasmunshi/euler/blob/master/docs/web-server-guide.md
After=network.target
# No Wants=/After= on euler-auth: the spool never talks to it. Identity comes from
# SO_PEERCRED and the profile from authorizations.json, so the two services have no
# ordering relationship to declare.

[Service]
# Type=simple, like every sibling kit: the app never sd_notify()s, so Type=notify would
# leave systemd waiting for a READY=1 that never comes.
Type=simple
User=${MSG_USER}
Group=${MSG_GROUP}
# euler-web: to reach the per-user instance sockets for the delivery nudge, and to
# chgrp its own public socket at bind time.
SupplementaryGroups=${WEB_GROUP}
EnvironmentFile=${MSG_ENV}
ExecStart=${VENV_PY} -m solver.web.msg
Restart=on-failure
RestartSec=5s

# State — euler-msg-only.
StateDirectory=euler-msg
StateDirectoryMode=0700

# The admin plane's own runtime dir (0700 euler-msg): root traverses it via sudo,
# nothing else does. /run/euler-adm is euler-auth's and is not writable here.
RuntimeDirectory=euler-msg
RuntimeDirectoryMode=0700

# Egress: none. This service has no network peer of any kind — AF_UNIX only, which
# makes "cannot reach the internet" a property of the process rather than of a rule
# it might be run without. Do not widen this to add a mail nudge without reading
# § Messaging — No mail.
IPAddressDeny=any
RestrictAddressFamilies=AF_UNIX

# Hardening.
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
# The shared socket dir is provisioned by tmpfiles.d (auth.sh) and owned by no service,
# so ProtectSystem=strict's read-only /run must be opened for the public socket.
ReadWritePaths=/run/euler
PrivateTmp=true
PrivateDevices=true
CapabilityBoundingSet=
LockPersonality=true
MemoryDenyWriteExecute=true
RestrictRealtime=true
SystemCallArchitectures=native
UMask=0007

[Install]
WantedBy=multi-user.target
EOF
    sudo systemctl daemon-reload
}

# ── deploy / remove / redeploy ─────────────────────────────────────────────────────

# `systemctl restart` returns as soon as the unit is active; the service binds its two
# sockets a beat later. do_status runs straight after, so without this wait it reports a
# perfectly healthy spool as "✗ missing / not answering" — the same false alarm the
# sudo-less `test -S` used to raise, from the other direction. Bounded, then give up and
# let do_status say what it finds.
wait_for_sockets() {
    local i
    for ((i = 0; i < 50; i++)); do
        if sudo test -S "${MSG_SOCKET}" && sudo test -S "${ADMIN_SOCKET}"; then return 0; fi
        sleep 0.1
    done
    return 0
}

do_deploy() {
    check_can_sudo || return 1
    require_systemd || return 1
    require_venv || return 1
    ensure_msg_user
    resolve_token
    deploy_msg_env
    deploy_state_dir
    deploy_unit
    if [ ! -f "${AUTHZ_FILE}" ]; then
        echo "Warning: ${AUTHZ_FILE} is absent — the spool maps nobody, so every verb"
        echo "         refuses until 'make deploy-auth' seeds the policy." >&2
    fi
    sudo systemctl enable --now "${SERVICE_NAME}"
    sudo systemctl restart "${SERVICE_NAME}"

    # The service uid joins the nftables egress drop set. The unit hardening already
    # makes off-host traffic impossible; this is defence in depth, because the chain is
    # policy-accept and an un-enumerated uid would reach the internet if the unit were
    # ever loosened.
    if [ -f /etc/systemd/system/euler-firewall.service ]; then
        echo "Reloading the egress firewall to include ${MSG_USER}..."
        "${SCRIPT_DIR}/firewall.sh" reload
    fi
    wait_for_sockets
    do_status
}

do_redeploy() {
    check_can_sudo || return 1
    require_venv || return 1
    echo "Restarting ${SERVICE_NAME} against ${VENV_DIR}..."
    sudo systemctl restart "${SERVICE_NAME}"
    wait_for_sockets
    do_status
}

do_remove() {
    check_can_sudo || return 1
    if [ -f "${SERVICE_DEST}" ]; then
        sudo systemctl disable --now "${SERVICE_NAME}" 2>/dev/null || true
        sudo rm -f "${SERVICE_DEST}"
        sudo systemctl daemon-reload
    fi
    sudo rm -f "${MSG_SOCKET}"

    local reply
    read -r -p "Remove ${STATE_DIR} (every message thread), ${MSG_ENV}, and the ${MSG_USER} user? [y/N] " reply
    if [[ "${reply}" =~ ^[Yy]$ ]]; then
        sudo rm -rf "${STATE_DIR}"
        sudo rm -f "${MSG_ENV}"
        if getent passwd "${MSG_USER}" > /dev/null; then sudo userdel "${MSG_USER}" 2>/dev/null || true; fi
        if getent group "${MSG_GROUP}" > /dev/null; then sudo groupdel "${MSG_GROUP}" 2>/dev/null || true; fi
    fi
    echo "Message service uninstall complete."
}

# ── status ─────────────────────────────────────────────────────────────────────────

# Probe the public socket's /healthz. Needs sudo: the socket is euler-web-only and the
# operator deliberately is not in that group.
probe_socket() {
    if ! command -v curl > /dev/null 2>&1; then
        echo "healthz:     … unknown (curl not installed)"
        return 0
    fi
    local reply
    reply="$(sudo curl -sS --max-time 3 --unix-socket "${MSG_SOCKET}" \
                  http://localhost/healthz 2>/dev/null || true)"
    if [ "${reply}" = "ok" ]; then
        echo "healthz:     ✓ ${MSG_SOCKET} serving"
    else
        echo "healthz:     ✗ ${MSG_SOCKET} not answering"
    fi
}

do_status() {
    if [ -f "${SERVICE_DEST}" ] && command -v systemctl &> /dev/null; then
        echo "${SERVICE_NAME}: $(systemctl is-active "${SERVICE_NAME}" 2>/dev/null)/$(systemctl is-enabled "${SERVICE_NAME}" 2>/dev/null)"
    else
        echo "${SERVICE_NAME}: ✗ not installed"
    fi
    if getent passwd "${MSG_USER}" > /dev/null; then
        echo "identity:    ✓ ${MSG_USER} (groups: $(id -nG "${MSG_USER}" 2>/dev/null))"
    else
        echo "identity:    ✗ ${MSG_USER} missing"
    fi
    if [ -f "${MSG_ENV}" ]; then
        echo "config:      ✓ ${MSG_ENV} ($(stat -c '%U:%G %a' "${MSG_ENV}" 2>/dev/null))"
    else
        echo "config:      ✗ ${MSG_ENV} missing"
    fi
    if [ -d "${STATE_DIR}" ]; then
        local threads
        threads="$(sudo "${PYTHON}" -c "import json,pathlib;p=pathlib.Path('${STATE_DIR}/messages.json');print(len(json.loads(p.read_text())) if p.exists() else 0)" 2>/dev/null || echo '?')"
        echo "spool:       ✓ ${STATE_DIR} ($(stat -c '%U:%G %a' "${STATE_DIR}" 2>/dev/null), ${threads} thread(s))"
    else
        echo "spool:       ✗ ${STATE_DIR} missing"
    fi
    # Under sudo, like the spool read above. The socket lives in a 0700 dir owned by
    # euler-msg, so a plain `test -S` from the operator's uid cannot traverse to it and
    # answers "missing" whatever the truth is — which it did, on a service that was serving
    # perfectly well, sending the operator hunting for a fault that was not there.
    if sudo test -S "${ADMIN_SOCKET}"; then
        echo "admin plane: ✓ ${ADMIN_SOCKET} (wheel-gated: sudo required)"
    else
        echo "admin plane: ✗ ${ADMIN_SOCKET} missing (service not running?)"
    fi
    if [ -f "${AUTHZ_FILE}" ]; then
        local staff
        staff="$(${PYTHON} -c "import json;u=json.load(open('${AUTHZ_FILE}')).get('users',{});print(sum(1 for p in u.values() if p in ('maintainer','admin')))" 2>/dev/null || echo '?')"
        echo "staff:       ✓ ${staff} identity(ies) at maintainer+ (the inbound queue's readers)"
    else
        echo "staff:       ✗ ${AUTHZ_FILE} missing — every verb refuses"
    fi
    probe_socket
}

# ── Dispatch ──────────────────────────────────────────────────────────────────────
ACTION="${1:-status}"
case "${ACTION}" in
    deploy)    do_deploy ;;
    upgrade)   do_deploy ;;
    redeploy)  do_redeploy ;;
    remove)    do_remove ;;
    status)    do_status ;;
    -h | --help | help) usage ;;
    *) echo "Unknown action: ${ACTION}"; usage; exit 1 ;;
esac

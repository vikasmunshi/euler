#!/usr/bin/env bash
# Auth service kit (euler-auth) — Phase 4, steps 2+ of the server redesign (DD-5/DD-6)
# ====================================================================================
#
# Installs / uninstalls / upgrades the runtime for the auth service: the service
# identities (euler-auth + the euler-adm admin group), the root-owned /opt/euler
# system venv the app services run from (DD-5), the scoped /etc/euler/auth.env,
# the /var/lib/euler-auth state dir (DD-6), and — once the solver.web.auth module
# exists in the deployed venv — the root-owned euler-auth.service. Sibling to
# frontend.sh / egress.sh / ddns.sh / firewall.sh / smtp.sh; see
# docs/server-redesign.md (Phase 4, DD-5..DD-9).
#
# Model:
#   - The app services run from a root-owned system venv at /opt/euler, NOT the
#     repo checkout: the service users cannot traverse the repo owner's 0750 home
#     (DD-5). install/upgrade does `pip install <repo>[web]` into it as root.
#   - euler-auth: own primary group (state files are euler-auth:euler-auth 0600),
#     supplementary member of euler-web (binds its sockets group euler-web in
#     /run/euler). euler-adm: the local admin-plane group — members (you) may
#     connect to /run/euler/auth-admin.sock (DD-6).
#   - /run/euler is provisioned via tmpfiles.d (root:euler-web 0770) so every app
#     service shares one socket dir without owning it.
#   - Scoped runtime config /etc/euler/auth.env (root:euler-auth 0640) is deployed
#     from keys/.env (the authoring source); EULER_ADMIN_TOKEN is generated into
#     keys/.env on first install. euler-auth never reads the full keys/.env.
#   - The systemd unit is installed only when solver.web.auth is importable from
#     the deployed venv (build-order step 4); until then install/upgrade report it
#     as deferred. Unit carries the DD-8 layer-1 filter (IPAddressDeny=any +
#     IPAddressAllow=localhost): the auth service is loopback-only by design.
#
#   /opt/euler/venv                        root:euler-web 0755  (deployed venv)
#   /etc/euler/auth.env                    root:euler-auth 0640 (generated here)
#   /var/lib/euler-auth                    euler-auth:euler-auth 0700 (state, DD-6)
#   /etc/tmpfiles.d/euler.conf             root:root 0644       (/run/euler socket dir)
#   /etc/systemd/system/euler-auth.service (root-owned, boot-enabled; deferred until
#                                           solver.web.auth exists in the venv)
#
# Because the unit lives in root's systemd and runs as a locked-down user, lifecycle
# (start/stop/restart) requires sudo (DD-3).
#
# Actions: install | uninstall | upgrade | status | help
#
# Author: Vikas Munshi <vikas.munshi@gmail.com>
# Copyright (c) 2026. All rights reserved.
# Licensed under the MIT License.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
ENV_FILE="${PROJECT_ROOT}/keys/.env"            # authoring source (operator-readable)

SYS_DIR="/etc/euler"
AUTH_ENV="${SYS_DIR}/auth.env"                  # scoped runtime config (root:euler-auth 0640)
OPT_DIR="/opt/euler"
VENV_DIR="${OPT_DIR}/venv"
VENV_PY="${VENV_DIR}/bin/python"
STATE_DIR="/var/lib/euler-auth"                 # DD-6: euler-auth-only state
TMPFILES_CONF="/etc/tmpfiles.d/euler.conf"      # /run/euler socket dir (DD-1/DD-5)

PYTHON="python3.14"                             # the project's floor; deadsnakes on 24.04

WEB_GROUP="euler-web"
AUTH_USER="euler-auth"
AUTH_GROUP="euler-auth"
ADM_GROUP="euler-adm"

# The loopback mail relay the auth service submits to (must match smtp.sh).
SMTP_RELAY="127.0.0.1:8025"

SERVICE_NAME="euler-auth.service"
SERVICE_DEST="/etc/systemd/system/${SERVICE_NAME}"

# Set by load_config.
FQDN=""
ADMIN_TOKEN=""
TERMS_VERSION=""

usage() {
    cat <<USAGE
Usage: $0 [install|uninstall|upgrade|status|help]

  install    Create euler-auth + euler-adm, build the /opt/euler system venv
             (pip install <repo>[web] as root), deploy /etc/euler/auth.env and
             /var/lib/euler-auth, and — when solver.web.auth exists in the venv —
             install the root-owned, boot-enabled euler-auth.service.
  uninstall  Remove the service + venv (prompts before removing auth.env, the
             state dir, and the users/groups).
  upgrade    Re-deploy the venv from the repo, refresh auth.env + unit, restart.
  status     Show venv/deps/identities/config/state/unit health.

  Authoring config in keys/.env: EULER_TLS_DOMAIN (base URL) and EULER_ADMIN_TOKEN
  (generated on first install), optional TERMS_VERSION. install deploys a scoped
  copy to ${AUTH_ENV} for ${AUTH_USER}.
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
        echo "Error: systemd is required for the auth service; it is not active here." >&2
        return 1
    fi
}

require_python() {
    if ! command -v "${PYTHON}" &> /dev/null; then
        echo "Error: ${PYTHON} not found — run 'make install-system' (deadsnakes) first." >&2
        return 1
    fi
}

# Source keys/.env (or the deployed auth.env) and resolve the FQDN + admin token.
# On install, a missing EULER_ADMIN_TOKEN is generated and appended to keys/.env so
# the authoring source and the deployed copy stay in sync (DD-6).
load_config() {
    local src=""
    if [ -r "${ENV_FILE}" ]; then
        src="${ENV_FILE}"
    elif [ -r "${AUTH_ENV}" ]; then
        src="${AUTH_ENV}"
    fi
    if [ -n "${src}" ]; then
        set -a
        # shellcheck disable=SC1090
        . "${src}"
        set +a
    fi
    FQDN="${EULER_TLS_DOMAIN:-}"
    ADMIN_TOKEN="${EULER_ADMIN_TOKEN:-}"
    TERMS_VERSION="${TERMS_VERSION:-1}"
    if [ -z "${FQDN}" ]; then
        echo "Error: EULER_TLS_DOMAIN not set in ${ENV_FILE}" >&2
        return 1
    fi
}

ensure_admin_token() {
    if [ -n "${ADMIN_TOKEN}" ]; then
        return 0
    fi
    if [ ! -w "${ENV_FILE}" ]; then
        echo "Error: EULER_ADMIN_TOKEN unset and ${ENV_FILE} is not writable" >&2
        return 1
    fi
    echo "Generating EULER_ADMIN_TOKEN into keys/.env (authoring source, DD-6)..."
    ADMIN_TOKEN="$(${PYTHON} -c 'import secrets; print(secrets.token_hex(32))')"
    printf '\n# Admin-plane shared secret for the auth service (X-Admin-Token, DD-6).\nEULER_ADMIN_TOKEN=%s\n' \
        "${ADMIN_TOKEN}" >> "${ENV_FILE}"
}

# Create the service identities (idempotent): euler-auth (own group, in euler-web)
# and the euler-adm admin-plane group with the invoking operator as a member.
ensure_identities() {
    if ! getent group "${WEB_GROUP}" > /dev/null; then
        sudo groupadd --system "${WEB_GROUP}"
    fi
    if ! getent group "${AUTH_GROUP}" > /dev/null; then
        sudo groupadd --system "${AUTH_GROUP}"
    fi
    if ! getent passwd "${AUTH_USER}" > /dev/null; then
        echo "Creating system user ${AUTH_USER} (group ${AUTH_GROUP}, +${WEB_GROUP})..."
        sudo useradd --system --no-create-home --shell /usr/sbin/nologin \
            -g "${AUTH_GROUP}" -G "${WEB_GROUP}" "${AUTH_USER}"
    fi
    if ! getent group "${ADM_GROUP}" > /dev/null; then
        sudo groupadd --system "${ADM_GROUP}"
    fi
    if ! id -nG "${USER}" | tr ' ' '\n' | grep -qx "${ADM_GROUP}"; then
        echo "Adding ${USER} to ${ADM_GROUP} (admin plane — re-login for it to take effect)..."
        sudo usermod -aG "${ADM_GROUP}" "${USER}"
    fi
}

# Build/refresh the root-owned system venv and install the repo (web extra) into it.
deploy_venv() {
    if [ ! -x "${VENV_PY}" ]; then
        echo "Creating system venv at ${VENV_DIR} (${PYTHON})..."
        sudo mkdir -p "${OPT_DIR}"
        sudo "${PYTHON}" -m venv "${VENV_DIR}"
    fi
    echo "Installing solver[web] into ${VENV_DIR} (as root, from ${PROJECT_ROOT})..."
    sudo "${VENV_PY}" -m pip install --quiet --upgrade pip
    sudo "${VENV_PY}" -m pip install --quiet "${PROJECT_ROOT}[web]"
    sudo chown -R root:"${WEB_GROUP}" "${OPT_DIR}"
    echo "Deployed: $(${VENV_PY} -c 'import solver, sys; print(f"solver in {sys.prefix}")' 2>/dev/null || echo '?')"
}

# /run/euler — the shared socket dir (root:euler-web 0770), via tmpfiles.d so it
# exists at boot before any service and no service owns it (DD-1/DD-5).
deploy_tmpfiles() {
    sudo tee "${TMPFILES_CONF}" > /dev/null <<EOF
# GENERATED by scripts/setup/auth.sh — shared unix-socket dir for the euler app
# services (DD-1/DD-5). Each service creates its own *.sock (0660 euler-<svc>:euler-web).
d /run/euler 0770 root ${WEB_GROUP} -
EOF
    sudo systemd-tmpfiles --create "${TMPFILES_CONF}"
}

# Deploy the scoped runtime config euler-auth reads (DD-6) — never the full keys/.env.
deploy_auth_env() {
    sudo mkdir -p "${SYS_DIR}"
    sudo tee "${AUTH_ENV}" > /dev/null <<EOF
# GENERATED by scripts/setup/auth.sh — scoped runtime config for euler-auth (DD-6).
# Authoring source: keys/.env. No Anthropic key, no SMTP creds (DD-8: mail goes to
# the loopback relay, which holds them).
EULER_BASE_URL=https://${FQDN}
EULER_ADMIN_TOKEN=${ADMIN_TOKEN}
TERMS_VERSION=${TERMS_VERSION}
EULER_SMTP_RELAY=${SMTP_RELAY}
EOF
    sudo chown root:"${AUTH_GROUP}" "${AUTH_ENV}"
    sudo chmod 0640 "${AUTH_ENV}"
}

# The euler-auth-only state dir (DD-6). The unit's StateDirectory= re-asserts this.
deploy_state_dir() {
    sudo mkdir -p "${STATE_DIR}"
    sudo chown "${AUTH_USER}:${AUTH_GROUP}" "${STATE_DIR}"
    sudo chmod 0700 "${STATE_DIR}"
}

# True when the deployed venv contains the auth service module (build-order step 4).
venv_has_auth() {
    [ -x "${VENV_PY}" ] && sudo "${VENV_PY}" -c 'import solver.web.auth' 2>/dev/null
}

# Install + enable the root-owned unit (only called when the module exists).
install_unit() {
    echo "Installing ${SERVICE_NAME} (loopback-only, as ${AUTH_USER})..."
    sudo tee "${SERVICE_DEST}" > /dev/null <<EOF
[Unit]
Description=euler auth service (SRP login, sessions, forward_auth — DD-5..DD-9)
Documentation=https://github.com/vikasmunshi/euler/blob/master/docs/server-redesign.md
After=network.target euler-smtp.service
Wants=euler-smtp.service

[Service]
Type=simple
User=${AUTH_USER}
Group=${AUTH_GROUP}
SupplementaryGroups=${WEB_GROUP}
EnvironmentFile=${AUTH_ENV}
ExecStart=${VENV_PY} -m solver.web.auth
Restart=on-failure
RestartSec=5s

# State (DD-6) — euler-auth-only.
StateDirectory=euler-auth
StateDirectoryMode=0700

# DD-8 layer 1: the auth service is loopback-only (sockets, Squid, the mail relay).
IPAddressDeny=any
IPAddressAllow=localhost

# Hardening.
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
PrivateDevices=true
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
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
    sudo systemctl enable --now "${SERVICE_NAME}"
    sudo systemctl restart "${SERVICE_NAME}"
}

# ── install / uninstall ───────────────────────────────────────────────────────────

do_install() {
    check_can_sudo || return 1
    require_systemd || return 1
    require_python || return 1
    load_config || return 1
    ensure_admin_token || return 1
    ensure_identities
    deploy_venv
    deploy_tmpfiles
    deploy_auth_env
    deploy_state_dir

    if venv_has_auth; then
        install_unit
    else
        echo "note: solver.web.auth not yet in the deployed package — service unit deferred"
        echo "      (re-run '$0 upgrade' once build-order step 4 lands)."
    fi

    # euler-auth's uid is part of the nftables egress ruleset — regenerate if installed.
    if [ -f /etc/systemd/system/euler-firewall.service ]; then
        echo "Reloading the egress firewall to include ${AUTH_USER}..."
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

    local reply
    read -r -p "Remove the ${VENV_DIR} venv? [y/N] " reply
    if [[ "${reply}" =~ ^[Yy]$ ]]; then
        sudo rm -rf "${OPT_DIR}"
        sudo rm -f "${TMPFILES_CONF}"
    fi
    read -r -p "Remove ${AUTH_ENV}, the ${STATE_DIR} state (user DB!), and the ${AUTH_USER}/${ADM_GROUP} identities? [y/N] " reply
    if [[ "${reply}" =~ ^[Yy]$ ]]; then
        sudo rm -f "${AUTH_ENV}"
        sudo rm -rf "${STATE_DIR}"
        if getent passwd "${AUTH_USER}" > /dev/null; then sudo userdel "${AUTH_USER}" 2>/dev/null || true; fi
        if getent group "${AUTH_GROUP}" > /dev/null; then sudo groupdel "${AUTH_GROUP}" 2>/dev/null || true; fi
        if getent group "${ADM_GROUP}" > /dev/null; then sudo groupdel "${ADM_GROUP}" 2>/dev/null || true; fi
    fi
    echo "Auth service uninstall complete."
}

# ── status ────────────────────────────────────────────────────────────────────────

do_status() {
    if [ -x "${VENV_PY}" ]; then
        echo "venv:        ✓ ${VENV_DIR} ($(${VENV_PY} --version 2>&1))"
        if "${VENV_PY}" -c 'import aiohttp, aiohttp_jinja2, jinja2, solver' 2>/dev/null; then
            echo "deps:        ✓ solver + aiohttp/aiohttp-jinja2/jinja2 importable"
        else
            echo "deps:        ✗ web deps or solver not importable from the venv"
        fi
    else
        echo "venv:        ✗ ${VENV_DIR} not deployed"
    fi
    local u
    for u in "${AUTH_USER}"; do
        if getent passwd "${u}" > /dev/null; then
            echo "identity:    ✓ ${u} (groups: $(id -nG "${u}" 2>/dev/null))"
        else
            echo "identity:    ✗ ${u} missing"
        fi
    done
    if getent group "${ADM_GROUP}" > /dev/null; then
        echo "admin plane: ✓ ${ADM_GROUP} (members: $(getent group "${ADM_GROUP}" | cut -d: -f4))"
    else
        echo "admin plane: ✗ ${ADM_GROUP} missing"
    fi
    if [ -f "${AUTH_ENV}" ]; then
        echo "config:      ✓ ${AUTH_ENV}"
    else
        echo "config:      ✗ ${AUTH_ENV} missing"
    fi
    if [ -d "${STATE_DIR}" ]; then
        echo "state:       ✓ ${STATE_DIR} ($(stat -c '%U:%G %a' "${STATE_DIR}" 2>/dev/null))"
    else
        echo "state:       ✗ ${STATE_DIR} missing"
    fi
    if [ -f "${SERVICE_DEST}" ]; then
        echo "${SERVICE_NAME}: $(systemctl is-active "${SERVICE_NAME}" 2>/dev/null)/$(systemctl is-enabled "${SERVICE_NAME}" 2>/dev/null)"
    else
        echo "${SERVICE_NAME}: deferred (solver.web.auth not yet deployed)"
    fi
}

# ── Dispatch ──────────────────────────────────────────────────────────────────────
ACTION="${1:-status}"
case "${ACTION}" in
    install)   do_install ;;
    upgrade)   do_install ;;
    uninstall) do_uninstall ;;
    status)    do_status ;;
    -h | --help | help) usage ;;
    *) echo "Unknown action: ${ACTION}"; usage; exit 1 ;;
esac

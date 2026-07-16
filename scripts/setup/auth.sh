#!/usr/bin/env bash
# Auth service kit (euler-auth) — Phase 4, steps 2+ of the server redesign (DD-5/DD-6)
# ====================================================================================
#
# Installs / uninstalls / upgrades the runtime for the auth service: the service
# identity (euler-auth) and wheel-gated admin plane, the root-owned /opt/euler
# system venv the app services run from (DD-5), the scoped /etc/euler/auth.env,
# the /var/lib/euler-auth state dir (DD-6), and — once the solver.web.auth module
# exists in the deployed venv — the root-owned euler-auth.service. Sibling to
# frontend.sh / egress.sh / ddns.sh / firewall.sh / smtp.sh; see
# docs/web-server-guide.md § Authentication.
#
# Model:
#   - The app services run from a root-owned system venv at /opt/euler, NOT the
#     repo checkout: the service users cannot traverse the repo owner's 0750 home
#     (DD-5). install/upgrade does `pip install <repo>[ai,dev,solutions,web]` into it
#     as root (the shared venv.sh helper — one definition for all app-service kits).
#   - euler-auth: own primary group (state files are euler-auth:euler-auth 0600),
#     supplementary member of euler-web (binds its public socket group euler-web
#     in /run/euler).
#   - The admin plane is WHEEL-GATED (DD-6): the admin socket is euler-auth-private
#     (0600, in /run/euler-adm) and EULER_ADMIN_TOKEN lives only in the
#     root-readable auth.env — the `users` command re-executes the admin CLI under
#     sudo. No admin group, no operator-held credentials.
#   - /run/euler (root:euler-web 0770) and /run/euler-adm (euler-auth 0750) are
#     provisioned via tmpfiles.d.
#   - Scoped runtime config /etc/euler/auth.env (root:euler-auth 0640) is deployed
#     from ~/.euler/env (the authoring source); EULER_ADMIN_TOKEN is generated
#     directly into auth.env (never ~/.euler/env) and preserved across upgrades.
#     euler-auth never reads the full ~/.euler/env.
#   - The systemd unit is installed only when solver.web.auth is importable from
#     the deployed venv (build-order step 4); until then install/upgrade report it
#     as deferred. Unit carries the DD-8 layer-1 filter (IPAddressDeny=any +
#     IPAddressAllow=localhost): the auth service is loopback-only by design.
#
#   /opt/euler/venv                        root:euler-web 0755  (deployed venv)
#   /etc/euler/auth.env                    root:euler-auth 0640 (generated here)
#   /etc/euler/authorizations.json         root:root 0644       (DD-12 SoR; seeded + migrated)
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
ENV_FILE="$(dirname "${PROJECT_ROOT}")/.$(basename "${PROJECT_ROOT}")/env"            # authoring source (operator-readable)

SYS_DIR="/etc/euler"
AUTH_ENV="${SYS_DIR}/auth.env"                  # scoped runtime config (root:euler-auth 0640)
AUTHZ_FILE="${SYS_DIR}/authorizations.json"     # DD-12 authorization SoR (root:root 0644)
AUTHZ_TEMPLATE="${PROJECT_ROOT}/solver/templates/authorizations.json"  # packaged bootstrap template (DD-12)
STATE_DIR="/var/lib/euler-auth"                 # DD-6: euler-auth-only state
TMPFILES_CONF="/etc/tmpfiles.d/euler.conf"      # /run/euler socket dir (DD-1/DD-5)

WEB_GROUP="euler-web"

# The system venv (DD-5) — OPT_DIR / VENV_DIR / VENV_PY / PYTHON / deploy_venv, shared
# by every app-service kit so the location + dependency set have one definition.
# shellcheck source=scripts/setup/venv.sh
. "${SCRIPT_DIR}/venv.sh"
AUTH_USER="euler-auth"
AUTH_GROUP="euler-auth"
LEGACY_ADM_GROUP="euler-adm"   # pre-wheel-gate admin group; removed on install/upgrade

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
Usage: $0 [install|uninstall|upgrade|redeploy|status|help]

  install    Create euler-auth, build the /opt/euler system venv (pip install
             <repo>[web] as root), deploy /etc/euler/auth.env (with a generated
             root-only EULER_ADMIN_TOKEN) and /var/lib/euler-auth, and — when
             solver.web.auth exists in the venv — install the root-owned,
             boot-enabled euler-auth.service.
  uninstall  Remove the service + venv (prompts before removing auth.env, the
             state dir, and the users/groups).
  upgrade    Re-deploy the venv from the repo, refresh auth.env + unit, restart.
  redeploy   Fast path: reinstall the repo into the /opt/euler venv (the shared
             code for auth AND content), re-merge the authorizations SoR, and
             restart the auth service — no identities, token, or unit changes.
  status     Show venv/deps/identities/config/state/unit health.

  Authoring config in ~/.euler/env: EULER_TLS_DOMAIN (base URL), optional
  TERMS_VERSION. The admin plane is wheel-gated: the admin socket and token are
  root-only, and the users shell command wraps its API calls in sudo.
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

# Source ~/.euler/env (or the deployed auth.env) and resolve the FQDN + admin token.
# On install, a missing EULER_ADMIN_TOKEN is generated and appended to ~/.euler/env so
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
    TERMS_VERSION="${TERMS_VERSION:-1}"
    if [ -z "${FQDN}" ]; then
        echo "Error: EULER_TLS_DOMAIN not set in ${ENV_FILE}" >&2
        return 1
    fi
}

# Resolve the admin token (root-only material, DD-6): preserve the one already
# deployed in auth.env, else generate afresh. Also scrub any legacy copy out of
# ~/.euler/env — the operator's uid must hold no admin credential.
ensure_admin_token() {
    ADMIN_TOKEN="$(sudo grep -s '^EULER_ADMIN_TOKEN=' "${AUTH_ENV}" 2>/dev/null | head -1 | cut -d= -f2- || true)"
    if [ -z "${ADMIN_TOKEN}" ]; then
        echo "Generating EULER_ADMIN_TOKEN (kept only in root-readable ${AUTH_ENV})..."
        ADMIN_TOKEN="$(${PYTHON} -c 'import secrets; print(secrets.token_hex(32))')"
    fi
    if [ -w "${ENV_FILE}" ] && grep -q '^EULER_ADMIN_TOKEN=' "${ENV_FILE}" 2>/dev/null; then
        echo "Scrubbing legacy EULER_ADMIN_TOKEN from ~/.euler/env (root-only material now)..."
        sed -i '/^# Admin-plane shared secret for the auth service (X-Admin-Token, DD-6)\.$/d;/^EULER_ADMIN_TOKEN=/d' \
            "${ENV_FILE}"
    fi
}

# Create the service identities (idempotent): euler-auth (own group, in euler-web).
# The admin plane is wheel-gated — no admin group; a legacy euler-adm from earlier
# installs is dismantled.
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
    else
        sudo usermod -aG "${WEB_GROUP}" "${AUTH_USER}"
    fi
    # Migration: drop the legacy admin group (the admin plane is sudo-gated now).
    if getent group "${LEGACY_ADM_GROUP}" > /dev/null; then
        echo "Removing legacy ${LEGACY_ADM_GROUP} group (admin plane is sudo-gated now)..."
        sudo gpasswd -d "${USER}" "${LEGACY_ADM_GROUP}" 2>/dev/null || true
        sudo gpasswd -d "${AUTH_USER}" "${LEGACY_ADM_GROUP}" 2>/dev/null || true
        sudo groupdel "${LEGACY_ADM_GROUP}" 2>/dev/null || true
    fi
}

# /run/euler — the shared socket dir (root:euler-web 0770), via tmpfiles.d so it
# exists at boot before any service and no service owns it (DD-1/DD-5).
deploy_tmpfiles() {
    sudo tee "${TMPFILES_CONF}" > /dev/null <<EOF
# GENERATED by scripts/setup/auth.sh — runtime socket dirs (DD-1/DD-5/DD-6).
# /run/euler: the shared app-service fabric; each service creates its own *.sock
#   (0660 euler-<svc>:euler-web). Operators are deliberately NOT in euler-web.
# /run/euler-adm: the local admin plane — euler-auth binds auth-admin.sock here
#   (0600); it is wheel-gated: only root (sudo) reaches it.
d /run/euler 0770 root ${WEB_GROUP} -
d /run/euler-adm 0750 ${AUTH_USER} ${AUTH_GROUP} -
EOF
    sudo systemd-tmpfiles --create "${TMPFILES_CONF}"
}

# Deploy the scoped runtime config euler-auth reads (DD-6) — never the full ~/.euler/env.
deploy_auth_env() {
    sudo mkdir -p "${SYS_DIR}"
    sudo tee "${AUTH_ENV}" > /dev/null <<EOF
# GENERATED by scripts/setup/auth.sh — scoped runtime config for euler-auth (DD-6).
# Authoring source: ~/.euler/env. No Anthropic key, no SMTP creds (DD-8: mail goes to
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

# Deploy the authorization system of record (DD-12, re-simplified): the policy is a
# plain profile ladder, so /etc/euler/authorizations.json (root:root 0644 —
# world-readable non-secret, root-write only) carries ONE decision: who has which
# profile. First deploy copies the repo template; every run seeds the checkout owner
# as `admin`, migrates any existing web accounts' profiles out of the
# euler-auth-private SRP DB into the map (old admin/user/guest → new
# maintainer/contributor/reader), and rewrites a legacy grants/objects-shaped file
# to the new {ladder, users} shape (the users map is the only thing carried over —
# the grant vocabulary is retired with the per-profile ACL layer).
deploy_authz() {
    local owner
    owner="$(stat -c '%U' "${PROJECT_ROOT}")"
    sudo mkdir -p "${SYS_DIR}"
    if [ ! -f "${AUTHZ_FILE}" ]; then
        echo "Deploying authorizations.json SoR from the repo template..."
        sudo install -m 0644 -o root -g root "${AUTHZ_TEMPLATE}" "${AUTHZ_FILE}"
    fi
    sudo "${PYTHON}" - "${AUTHZ_FILE}" "${owner}" "${STATE_DIR}/users.json" "${AUTHZ_TEMPLATE}" <<'PY'
import json, pathlib, sys
authz_path, owner, users_path, template_path = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
authz = json.loads(pathlib.Path(authz_path).read_text())
users = dict(authz.get('users', {}))
users.setdefault(owner, 'admin')                         # local owner anchor (seeded for visibility)
migrate = {'admin': 'maintainer', 'user': 'contributor', 'guest': 'reader'}
try:                                                     # migrate existing web accounts from the SRP DB
    srp = json.loads(pathlib.Path(users_path).read_text()).get('users', {})
except (OSError, json.JSONDecodeError):
    srp = {}
for email, rec in srp.items():
    if email not in users:
        old = str(rec.get('profile', 'user'))
        users[email] = migrate.get(old, old)             # already-new names pass through
# Re-simplified policy (plain profile floors): the file carries ONE decision — who
# has which profile. A legacy grants/objects-shaped file is rewritten to the new
# shape here, its users map carried over; the retired sections are dropped (they
# only ever drove the per-profile content-tree ACLs, gone with the per-user model).
template = json.loads(pathlib.Path(template_path).read_text())
if 'profiles' in authz or 'objects' in authz:
    print('authorizations.json: migrating the legacy grants/objects shape → plain profile ladder')
new = {'ladder': template.get('ladder', ['reader', 'contributor', 'maintainer', 'admin']),
       'users': dict(sorted(users.items()))}
pathlib.Path(authz_path).write_text(json.dumps(new, indent=2) + '\n')
print(f'authorizations.json: {len(users)} user(s) mapped (owner {owner}=admin)')
PY
    sudo chown root:root "${AUTHZ_FILE}"
    sudo chmod 0644 "${AUTHZ_FILE}"
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
Documentation=https://github.com/vikasmunshi/euler/blob/master/docs/web-server-guide.md
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

# Hardening. ProtectSystem=strict mounts /run read-only, so the shared socket
# dir (provisioned by tmpfiles.d, not RuntimeDirectory= — no service owns it)
# must be opened up explicitly for the service's two sockets.
NoNewPrivileges=true
ProtectSystem=strict
ReadWritePaths=/run/euler /run/euler-adm
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
    deploy_venv "${PROJECT_ROOT}" "${WEB_GROUP}"
    deploy_tmpfiles
    deploy_auth_env
    deploy_state_dir
    deploy_authz

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

# Fast redeploy: reinstall the repo into the shared /opt/euler venv (refreshing the
# code for both auth and content), re-merge the authorizations SoR (picks up new
# template objects/grants), and restart the auth service. No identities, admin
# token, tmpfiles, state dir, unit re-lay, or firewall reload.
do_redeploy() {
    check_can_sudo || return 1
    require_python || return 1
    load_config || return 1
    deploy_venv "${PROJECT_ROOT}" "${WEB_GROUP}"
    deploy_authz
    if [ -f "${SERVICE_DEST}" ] && venv_has_auth; then
        sudo systemctl restart "${SERVICE_NAME}"
        echo "Restarted ${SERVICE_NAME}"
    else
        echo "note: ${SERVICE_NAME} not installed yet — run '$0 install'."
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
    read -r -p "Remove ${AUTH_ENV} (admin token), the ${STATE_DIR} state (user DB!), and the ${AUTH_USER} identity? [y/N] " reply
    if [[ "${reply}" =~ ^[Yy]$ ]]; then
        sudo rm -f "${AUTH_ENV}" "${AUTHZ_FILE}"
        sudo rm -rf "${STATE_DIR}"
        if getent passwd "${AUTH_USER}" > /dev/null; then sudo userdel "${AUTH_USER}" 2>/dev/null || true; fi
        if getent group "${AUTH_GROUP}" > /dev/null; then sudo groupdel "${AUTH_GROUP}" 2>/dev/null || true; fi
        if getent group "${LEGACY_ADM_GROUP}" > /dev/null; then sudo groupdel "${LEGACY_ADM_GROUP}" 2>/dev/null || true; fi
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
    if getent passwd "${AUTH_USER}" > /dev/null; then
        echo "identity:    ✓ ${AUTH_USER} (groups: $(id -nG "${AUTH_USER}" 2>/dev/null))"
    else
        echo "identity:    ✗ ${AUTH_USER} missing"
    fi
    if [ -d /run/euler-adm ]; then
        echo "admin plane: ✓ /run/euler-adm (wheel-gated: sudo required; no admin group)"
    else
        echo "admin plane: ✗ /run/euler-adm missing (tmpfiles not applied)"
    fi
    if [ -f "${AUTH_ENV}" ]; then
        echo "config:      ✓ ${AUTH_ENV}"
    else
        echo "config:      ✗ ${AUTH_ENV} missing"
    fi
    if [ -f "${AUTHZ_FILE}" ]; then
        echo "authz:       ✓ ${AUTHZ_FILE} ($(python3 -c "import json;print(len(json.load(open('${AUTHZ_FILE}')).get('users',{})))" 2>/dev/null || echo '?') users)"
    else
        echo "authz:       ✗ ${AUTHZ_FILE} missing (local shell uses the repo template)"
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
    redeploy)  do_redeploy ;;
    uninstall) do_uninstall ;;
    status)    do_status ;;
    -h | --help | help) usage ;;
    *) echo "Unknown action: ${ACTION}"; usage; exit 1 ;;
esac

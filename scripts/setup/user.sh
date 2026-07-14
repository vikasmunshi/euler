#!/usr/bin/env bash
# Per-user provisioning kit (euler-user) — step 3 of the multi-tenant redesign (MT-7)
# ==============================================================================
#
# Installs / uninstalls the OS layer for the **per-user** web tier, and provisions
# or tears down one collaborator at a time. This replaces the per-*profile*
# shared-uid model (ws.sh / content.sh, DD-13): instead of three fixed rungs sharing
# a uid, every collaborator gets their **own** uid, home, and repo clone, so their
# own keys can rest in their own uid-private home without leaking to anyone else.
# Design of record: docs/real-multi-tenant-web-access.md (MT-3/MT-4/MT-7/MT-13).
#
# Two planes:
#
#   install / uninstall / status  — the SHARED layer, once per host:
#     - the euler-user parent group (egress + traversal);
#     - a shared bare mirror /var/lib/euler/mirror.git — one ciphertext object
#       store every per-user clone hardlinks from, refreshed from the operator's
#       working tree (MT-13). Objects in git are always ciphertext, so the mirror
#       never holds plaintext;
#     - /etc/euler/user.env (scoped runtime config, no secrets);
#     - the socket-activated euler-user@.service + euler-user@.socket template,
#       deferred until solver.web.user lands in the /opt/euler venv (step 4), exactly
#       as ws.sh defers its unit until solver.web.ws exists.
#
#   provision / deprovision <slug>  — ONE collaborator:
#     provision   create euler-user-<slug> + home (0700), clone the repo into
#                 ~/euler on branch user/<slug> with the crypt filter DISABLED (so
#                 solutions/private/** stays ciphertext at rest — the filter is wired
#                 later, in the web shell, once the user is key-authorized, §6), lay
#                 down ~/.euler (0700, secrets dir), and enable the instance socket.
#     deprovision stop + disable the instance, then (prompted) userdel + remove the
#                 home. Dropping the account's master-key access is a SEPARATE admin
#                 crypto act (`key-rekey`), reported here — it needs the master key,
#                 which this root-plane script deliberately never touches.
#
# Why the clone lands ciphertext for free: the crypt filter is registered in the
# clone's LOCAL git config (never cloned) plus a TRACKED .gitattributes rule. A fresh
# clone therefore inherits the attribute but not the filter definition, so encrypted
# blobs pass through untouched — plaintext only appears once the user runs the filter
# install with their own key (solver.crypto.gitfilter). No secret is provisioned here.
#
# Because the units live in root's systemd and run as locked-down users, lifecycle
# requires sudo (DD-3).
#
# Actions: install | uninstall | upgrade | redeploy | provision | deprovision | status | help
#
# Author: Vikas Munshi <vikas.munshi@gmail.com>
# Copyright (c) 2026. All rights reserved.
# Licensed under the MIT License.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
HOME_DIR="$(dirname "${PROJECT_ROOT}")"                # the operator home the repo lives in

SYS_DIR="/etc/euler"
USER_ENV="${SYS_DIR}/user.env"                         # scoped runtime config (root:euler-web 0640)
EGRESS_ENV="${SYS_DIR}/egress.env"                     # HTTPS_PROXY (egress.sh)

WEB_GROUP="euler-web"
USER_GROUP="euler-user"                                # parent group: every per-user uid joins it
STATE_LIB="/var/lib/euler"
MIRROR="${STATE_LIB}/mirror.git"                       # shared ciphertext object store (MT-13)
USER_HOME_BASE="/home"                                 # euler-user-<slug> homes live here

SERVICE_TEMPLATE="euler-user@.service"
SOCKET_TEMPLATE="euler-user@.socket"
SERVICE_DEST="/etc/systemd/system/${SERVICE_TEMPLATE}"
SOCKET_DEST="/etc/systemd/system/${SOCKET_TEMPLATE}"

# The system venv (DD-5) — OPT_DIR / VENV_DIR / VENV_PY / PYTHON / deploy_venv.
# shellcheck source=scripts/setup/venv.sh
. "${SCRIPT_DIR}/venv.sh"

usage() {
    cat <<USAGE
Usage: $0 <action> [args]

  install                      Create the euler-user group, the shared bare mirror,
                               /etc/euler/user.env, and — when solver.web.user is in
                               the /opt/euler venv — the euler-user@.service/.socket
                               template. Idempotent.
  uninstall                    Remove the template + user.env + mirror (prompted).
                               Provisioned users must be deprovisioned first.
  upgrade                      Re-assert the shared layer and refresh the mirror.
  redeploy                     Refresh /etc/euler/user.env and the mirror only.
  provision <slug> <email> <profile>
                               Provision one collaborator: uid + home (0700), a
                               filter-disabled clone on branch user/<slug>, ~/.euler,
                               and the instance socket. Idempotent.
  deprovision <slug>           Tear one collaborator down: stop/disable the instance,
                               then (prompted) userdel + remove the home. Reports the
                               required 'key-rekey' to drop master-key access.
  status [<slug>]              Show the shared layer, or one user's instance health.

  Requires: the /opt/euler venv (auth.sh). The Caddy X-User-Slug routing that dials
  these sockets is wired by frontend.sh in step 4 (the per-user service).
USAGE
}

# ── guards ──────────────────────────────────────────────────────────────────────────

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
        echo "Error: systemd is required for the per-user service; it is not active here." >&2
        return 1
    fi
}

require_python() {
    if ! command -v "${PYTHON}" &> /dev/null; then
        echo "Error: ${PYTHON} not found — run 'make install-system' (deadsnakes) first." >&2
        return 1
    fi
}

# A slug is exactly what solver.auth.identity.system_slug emits: a useradd-safe name,
# letter-led, [a-z0-9-] only (MT-14). Refuse anything else — this value becomes a uid,
# a home path, a socket name, and a git branch, so it must not carry surprises.
valid_slug() {
    [[ "$1" =~ ^[a-z][a-z0-9-]*$ ]] && [ ${#1} -le 20 ]
}

require_slug() {
    if ! valid_slug "${1:-}"; then
        echo "Error: '${1:-}' is not a valid system slug (expected ^[a-z][a-z0-9-]*\$, <=20)." >&2
        echo "       The slug comes from solver.auth.identity.system_slug(email)." >&2
        return 1
    fi
}

# ── shared layer ──────────────────────────────────────────────────────────────────────

ensure_shared_groups() {
    getent group "${WEB_GROUP}"  > /dev/null || sudo groupadd --system "${WEB_GROUP}"
    getent group "${USER_GROUP}" > /dev/null || sudo groupadd --system "${USER_GROUP}"
}

# Deploy the shared /opt/euler venv (venv.sh); the per-user service module (step 4)
# imports from it. Same probe shape as ws.sh; solver.web.user is expected to be absent
# until step 4, and the unit install is gated on it.
deploy_user_venv() {
    deploy_venv "${PROJECT_ROOT}" "${WEB_GROUP}"
    if sudo "${VENV_PY}" -P -c 'import solver.web.user' 2>/dev/null; then
        echo "Deployed: ✓ solver.web.user importable from ${VENV_DIR}"
    else
        echo "Deployed: … solver.web.user not in the venv yet (step 4) — unit deferred"
    fi
}

# The shared bare mirror: one ciphertext object store every per-user clone hardlinks
# from (MT-13). Created from — and refreshed from — the operator's working tree, which
# the operator keeps synced with origin/master by their normal git workflow. No network
# and no credentials on this path: git objects are ciphertext, and the operator already
# owns the plaintext tree.
ensure_mirror() {
    sudo mkdir -p "${STATE_LIB}"
    if [ -d "${MIRROR}" ]; then
        echo "Refreshing the shared mirror ${MIRROR} from ${PROJECT_ROOT}..."
        sudo git -C "${MIRROR}" fetch --prune "${PROJECT_ROOT}" '+refs/heads/*:refs/heads/*'
    else
        echo "Creating the shared bare mirror ${MIRROR} from ${PROJECT_ROOT}..."
        sudo git clone --bare "${PROJECT_ROOT}" "${MIRROR}"
    fi
    sudo chown -R root:"${USER_GROUP}" "${MIRROR}"
    sudo chmod -R g+rX "${MIRROR}"
}

# Scoped runtime config for the per-user instances. No ANTHROPIC_API_KEY and no master
# key: each user brings their own, in their own vault (MT-6). The per-instance
# EULER_REPO_ROOT / EULER_USER_SLUG / socket come from the template unit (%i).
deploy_user_env() {
    sudo mkdir -p "${SYS_DIR}"
    sudo tee "${USER_ENV}" > /dev/null <<EOF
# GENERATED by scripts/setup/user.sh — scoped runtime config for euler-user (MT-7).
# The per-instance EULER_REPO_ROOT, EULER_USER_SLUG and socket are set by the unit (%i).
# No credentials here, deliberately: each user's secrets live in their own vault (MT-6),
# unwrapped per-session from their own home — nothing operator-owned reaches this tier.
EULER_AUTH_SOCKET=/run/euler/auth.sock
EULER_WEB_GROUP=${WEB_GROUP}
EOF
    sudo chown root:"${WEB_GROUP}" "${USER_ENV}"
    sudo chmod 0640 "${USER_ENV}"
}

venv_has_user_service() {
    [ -x "${VENV_PY}" ] && sudo "${VENV_PY}" -P -c 'import solver.web.user' 2>/dev/null
}

# The socket-activated template: one euler-user@<slug> instance per collaborator, each
# born as its own uid (no setuid, no root), on its own /run/euler/user-<slug>.sock that
# Caddy dials by the forward_auth X-User-Slug (MT-4/MT-11). Serves BOTH the content
# routes and /ws — one service, not the DD-13 content@/ws@ split.
install_units() {
    echo "Installing ${SOCKET_TEMPLATE} + ${SERVICE_TEMPLATE} (socket-activated, per-user)..."
    sudo tee "${SOCKET_DEST}" > /dev/null <<EOF
[Unit]
Description=euler per-user instance socket (%i) — the collaborator's content + /ws (MT-4)
Documentation=https://github.com/vikasmunshi/euler/blob/master/docs/real-multi-tenant-web-access.md

[Socket]
ListenStream=/run/euler/user-%i.sock
SocketMode=0660
SocketUser=euler-user-%i
SocketGroup=${WEB_GROUP}
# Caddy (euler-caddy, in ${WEB_GROUP}) connects; the instance is spawned on demand.

[Install]
WantedBy=sockets.target
EOF

    sudo tee "${SERVICE_DEST}" > /dev/null <<EOF
[Unit]
Description=euler per-user instance (%i) — one collaborator's content + web shell (MT-4/MT-7)
Documentation=https://github.com/vikasmunshi/euler/blob/master/docs/real-multi-tenant-web-access.md
After=network.target euler-auth.service
Wants=euler-auth.service
Requires=euler-user@%i.socket

[Service]
Type=notify
# Born as the collaborator's own uid — no setuid, no root. The uid owns its home,
# its clone, and its vault; the kernel (SO_PEERCRED) is the authoritative identity.
User=euler-user-%i
EnvironmentFile=${USER_ENV}
# HTTPS_PROXY: the problem scraper egresses only through Squid (DD-8/Phase 2).
EnvironmentFile=-${EGRESS_ENV}
Environment=EULER_USER_SLUG=%i
Environment=EULER_REPO_ROOT=${USER_HOME_BASE}/euler-user-%i/euler
ExecStart=${VENV_PY} -m solver.web.user
Restart=on-failure
RestartSec=5s

# DD-8 layer 1: loopback only — the /run/euler sockets and the Squid proxy. The kernel
# firewall (firewall.sh, scoped to the euler-user-* uids) is layer 2.
IPAddressDeny=any
IPAddressAllow=localhost

# Hardening. This tier runs the user's own code by design (AR-1/MT-6b), contained to
# THIS user's uid — their home, their keys, their clone, no one else's. The sandbox
# must not break the code being run (native extensions need W^X), so containment is the
# uid + egress lock, not a syscall jail.
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=false
ReadWritePaths=/run/euler ${USER_HOME_BASE}/euler-user-%i
PrivateTmp=true
PrivateDevices=true
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
CapabilityBoundingSet=
LockPersonality=true
RestrictRealtime=true
SystemCallArchitectures=native
UMask=0007

# One PTY child per attached tab; the cgroup kill collects them all on stop.
KillMode=control-group
TimeoutStopSec=20s

[Install]
WantedBy=multi-user.target
EOF
    sudo systemctl daemon-reload
}

# ── per-user provision / deprovision ──────────────────────────────────────────────────

user_of()  { echo "euler-user-$1"; }
home_of()  { echo "${USER_HOME_BASE}/euler-user-$1"; }
sock_of()  { echo "/run/euler/user-$1.sock"; }

ensure_user_identity() {
    local slug="$1" user home
    user="$(user_of "${slug}")"
    home="$(home_of "${slug}")"
    if ! getent passwd "${user}" > /dev/null; then
        echo "Creating system user ${user} (home ${home}, group ${USER_GROUP})..."
        sudo useradd --system --create-home --home-dir "${home}" \
            --shell /usr/sbin/nologin -U -G "${WEB_GROUP},${USER_GROUP}" "${user}"
    else
        sudo usermod -G "${WEB_GROUP},${USER_GROUP}" "${user}"
    fi
    sudo chmod 0700 "${home}"
    # ~/.euler — the uid-private secrets dir (matches solver.config root.parent/.{name}
    # for root=~/euler). Empty now; the user's key + vault land here later, self-service.
    sudo install -d -m 0700 -o "${user}" -g "${user}" "${home}/.euler"
}

# Clone the repo into ~/euler on branch user/<slug>, filter DISABLED → ciphertext at
# rest. Clone from the shared mirror (local, hardlinked objects, no credentials); repoint
# origin at the real remote so the user can push user/<slug> as themselves later (MT-2).
provision_clone() {
    local slug="$1" user home clone origin_url
    user="$(user_of "${slug}")"
    home="$(home_of "${slug}")"
    clone="${home}/euler"
    if [ -d "${clone}/.git" ]; then
        echo "Clone ${clone} already present — leaving it in place."
        return 0
    fi
    if [ ! -d "${MIRROR}" ]; then
        echo "Error: shared mirror ${MIRROR} missing — run '$0 install' first." >&2
        return 1
    fi
    origin_url="$(git -C "${PROJECT_ROOT}" remote get-url origin 2>/dev/null || echo "${PROJECT_ROOT}")"
    echo "Cloning into ${clone} (filter disabled → ciphertext at rest)..."
    # No filter is wired in the clone's local config, and .gitattributes' rule is not
    # 'required', so solutions/private/** checks out as the ciphertext held in git.
    sudo git clone --branch master "${MIRROR}" "${clone}"
    sudo git -C "${clone}" remote set-url origin "${origin_url}"
    sudo git -C "${clone}" checkout -B "user/${slug}"
    sudo chown -R "${user}:${user}" "${clone}"
}

enable_socket() {
    local slug="$1"
    if [ ! -f "${SOCKET_DEST}" ]; then
        echo "note: euler-user@.socket not installed yet (solver.web.user pending, step 4) —"
        echo "      instance socket for ${slug} deferred; re-run '$0 upgrade' then provision."
        return 0
    fi
    sudo systemctl enable --now "euler-user@${slug}.socket"
}

do_provision() {
    local slug="${1:-}" email="${2:-}" profile="${3:-reader}"
    require_slug "${slug}" || return 1
    check_can_sudo || return 1
    require_python || return 1
    ensure_shared_groups
    if [ ! -d "${MIRROR}" ]; then
        echo "Error: run '$0 install' before provisioning (shared mirror + config missing)." >&2
        return 1
    fi
    ensure_user_identity "${slug}"
    provision_clone "${slug}"
    enable_socket "${slug}"
    # The new uid must be inside the egress lock, or (chain policy accept) it would reach
    # the internet directly, bypassing Squid. firewall.sh enumerates euler-user-* by group.
    if [ -f /etc/systemd/system/euler-firewall.service ]; then
        echo "Reloading the egress firewall to cover $(user_of "${slug}")..."
        "${SCRIPT_DIR}/firewall.sh" reload || echo "warn: firewall reload failed — run 'make upgrade-firewall'"
    fi
    echo "Provisioned ${slug}${email:+ (}${email}${email:+)} → profile ${profile}."
    echo "Next (self-service, in the user's web shell): generate a key (\`user\`), have an"
    echo "admin \`user-authorize\` it + push, then \`git pull\` to smudge their private tree."
}

do_deprovision() {
    local slug="${1:-}" user home reply
    require_slug "${slug}" || return 1
    check_can_sudo || return 1
    user="$(user_of "${slug}")"
    home="$(home_of "${slug}")"

    if [ -f "${SOCKET_DEST}" ]; then
        sudo systemctl disable --now "euler-user@${slug}.socket"  2>/dev/null || true
        sudo systemctl disable --now "euler-user@${slug}.service" 2>/dev/null || true
    fi
    sudo rm -f "$(sock_of "${slug}")"

    echo
    echo "IMPORTANT: this does NOT revoke ${slug}'s master-key access. If their key was"
    echo "           user-authorized, run \`key-rekey\` in the shell to rotate the master key"
    echo "           and re-wrap it to the remaining authorized users only (their key was"
    echo "           never on this root plane, so it cannot be dropped from here)."
    echo

    if ! getent passwd "${user}" > /dev/null; then
        echo "No such user ${user} — nothing more to remove."
        return 0
    fi
    read -r -p "Remove the account ${user} and its home ${home}? [y/N] " reply
    if [[ "${reply}" =~ ^[Yy]$ ]]; then
        sudo userdel --remove "${user}" 2>/dev/null || sudo userdel "${user}" 2>/dev/null || true
        getent group "${user}" > /dev/null && sudo groupdel "${user}" 2>/dev/null || true
        sudo rm -rf "${home}"
        echo "Removed ${user} and ${home}."
    else
        echo "Left ${user} in place (instance stopped/disabled). Home: ${home}."
    fi
    if [ -f /etc/systemd/system/euler-firewall.service ]; then
        "${SCRIPT_DIR}/firewall.sh" reload 2>/dev/null || true
    fi
}

# ── install / uninstall / status ──────────────────────────────────────────────────────

do_install() {
    check_can_sudo || return 1
    require_systemd || return 1
    require_python || return 1
    ensure_shared_groups
    deploy_user_venv
    ensure_mirror
    deploy_user_env
    sudo mkdir -p /run/euler

    if venv_has_user_service; then
        install_units
    else
        echo "note: solver.web.user not yet in the deployed package — unit template deferred"
        echo "      (re-run '$0 upgrade' once step 4 lands the service)."
    fi
    do_status
}

do_redeploy() {
    check_can_sudo || return 1
    deploy_user_env
    ensure_mirror
    echo "Refreshed ${USER_ENV} and the shared mirror."
    do_status
}

do_uninstall() {
    check_can_sudo || return 1
    # Any provisioned users left? Refuse to strip the shared layer out from under them.
    local leftover
    leftover="$(getent passwd | awk -F: '/^euler-user-/{print $1}' || true)"
    if [ -n "${leftover}" ]; then
        echo "Refusing to uninstall — provisioned users remain:" >&2
        echo "${leftover}" | sed 's/^/  /' >&2
        echo "Deprovision each ('$0 deprovision <slug>') first." >&2
        return 1
    fi
    if [ -f "${SOCKET_DEST}" ] || [ -f "${SERVICE_DEST}" ]; then
        sudo rm -f "${SOCKET_DEST}" "${SERVICE_DEST}"
        sudo systemctl daemon-reload
    fi
    sudo rm -f "${USER_ENV}"

    local reply
    read -r -p "Remove the shared mirror ${MIRROR}? [y/N] " reply
    [[ "${reply}" =~ ^[Yy]$ ]] && sudo rm -rf "${MIRROR}"
    read -r -p "Remove the ${USER_GROUP} group? [y/N] " reply
    [[ "${reply}" =~ ^[Yy]$ ]] && { getent group "${USER_GROUP}" > /dev/null && sudo groupdel "${USER_GROUP}" 2>/dev/null || true; }
    echo "Per-user provisioning uninstall complete."
}

do_status() {
    if [ -x "${VENV_PY}" ]; then
        if "${VENV_PY}" -P -c 'import solver.web.user' 2>/dev/null; then
            echo "venv:        ✓ solver.web.user importable from ${VENV_DIR}"
        else
            echo "venv:        … solver.web.user not in the venv yet (step 4)"
        fi
    else
        echo "venv:        ✗ ${VENV_DIR} not deployed (run auth.sh / user.sh install)"
    fi
    getent group "${USER_GROUP}" > /dev/null \
        && echo "group:       ✓ ${USER_GROUP}" || echo "group:       ✗ ${USER_GROUP} missing"
    [ -d "${MIRROR}" ] && echo "mirror:      ✓ ${MIRROR}" || echo "mirror:      ✗ ${MIRROR} missing"
    [ -f "${USER_ENV}" ] && echo "config:      ✓ ${USER_ENV}" || echo "config:      ✗ ${USER_ENV} missing"
    if [ -f "${SOCKET_DEST}" ]; then
        echo "template:    ✓ ${SOCKET_TEMPLATE} + ${SERVICE_TEMPLATE}"
    else
        echo "template:    deferred (solver.web.user not yet deployed)"
    fi

    # Per-user roster (or one slug's instance).
    local slug="${1:-}"
    if [ -n "${slug}" ]; then
        status_one "${slug}"
        return 0
    fi
    local users u
    users="$(getent passwd | awk -F: '/^euler-user-/{print $1}' || true)"
    if [ -z "${users}" ]; then
        echo "users:       (none provisioned)"
        return 0
    fi
    for u in ${users}; do
        status_one "${u#euler-user-}"
    done
}

status_one() {
    local slug="$1" user home sock health="—"
    user="$(user_of "${slug}")"
    home="$(home_of "${slug}")"
    sock="$(sock_of "${slug}")"
    if ! getent passwd "${user}" > /dev/null; then
        echo "user ${slug}: ✗ ${user} missing"
        return 0
    fi
    if [ -f "${SOCKET_DEST}" ]; then
        health="$(systemctl is-active "euler-user@${slug}.socket" 2>/dev/null || echo inactive)"
    fi
    local clone_state="no-clone"
    [ -d "${home}/euler/.git" ] && clone_state="clone✓"
    echo "user ${slug}: ✓ ${user} · ${clone_state} · socket ${health}"
}

# ── Dispatch ──────────────────────────────────────────────────────────────────────────
ACTION="${1:-status}"
shift || true
case "${ACTION}" in
    install)     do_install ;;
    upgrade)     do_install ;;
    redeploy)    do_redeploy ;;
    uninstall)   do_uninstall ;;
    provision)   do_provision "$@" ;;
    deprovision) do_deprovision "$@" ;;
    status)      do_status "$@" ;;
    -h | --help | help) usage ;;
    *) echo "Unknown action: ${ACTION}"; usage; exit 1 ;;
esac

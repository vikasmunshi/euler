#!/usr/bin/env bash
# Per-user provisioning kit (euler-user) — step 3 of the multi-tenant redesign (MT-7)
# ==============================================================================
#
# Installs / uninstalls the OS layer for the **per-user** web tier, and provisions
# or tears down one collaborator at a time. This replaces the per-*profile*
# shared-uid model (DD-13): instead of three fixed rungs sharing a uid, every
# collaborator gets their **own** uid, home, and repo clone, so their
# own keys can rest in their own uid-private home without leaking to anyone else.
# Design of record: docs/web-server-guide.md § The per-user tier.
#
# Two planes:
#
#   install / uninstall / status  — the SHARED layer, once per host:
#     - the euler-user parent group (egress + traversal);
#     - /etc/euler/user.env (scoped runtime config, no secrets);
#     - the socket-activated euler-user@.service + euler-user@.socket template,
#       deferred until solver.web.user lands in the /opt/euler venv (step 4).
#
#   provision / deprovision <slug>  — ONE collaborator:
#     provision   create euler-user-<slug> + home (0700), clone ~/euler DIRECTLY from
#                 the public GitHub repo (anonymous read — no credentials) on branch
#                 user/<slug> with the crypt filter DISABLED (so solutions/private/**
#                 stays ciphertext at rest — GitHub holds only the filter's ciphertext,
#                 and the filter is wired later, in the web shell, once the user is
#                 key-authorized, §6), lay down ~/.euler (0700, secrets dir), and enable
#                 the instance socket.
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

SYS_DIR="/etc/euler"
USER_ENV="${SYS_DIR}/user.env"                         # scoped runtime config (root:euler-web 0640)
EGRESS_ENV="${SYS_DIR}/egress.env"                     # HTTPS_PROXY (egress.sh)

WEB_GROUP="euler-web"
USER_GROUP="euler-user"                                # parent group: every per-user uid joins it
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

  install                      Create the euler-user group, /etc/euler/user.env, and —
                               when solver.web.user is in the /opt/euler venv — the
                               euler-user@.service/.socket template. Idempotent.
  uninstall                    Remove the template + user.env (prompted). Provisioned
                               users must be deprovisioned first.
  upgrade                      Re-assert the shared layer.
  redeploy                     Refresh /etc/euler/user.env and stop the running
                               instances so their sockets re-activate them against a
                               freshly rebuilt venv (drops live shells).
  provision <slug> <email> <profile>
                               Provision one collaborator: uid + home (0700), a
                               filter-disabled clone of ~/euler from the public GitHub
                               repo on branch user/<slug> (cloned AS the user, through
                               Squid), git hooks, Claude Code (~/.local/bin, theirs),
                               ~/.euler, and the instance socket. Idempotent.
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
# imports from it. solver.web.user is expected to be absent until step 4, and the
# unit install is gated on it.
deploy_user_venv() {
    deploy_venv "${PROJECT_ROOT}" "${WEB_GROUP}"
    if sudo "${VENV_PY}" -P -c 'import solver.web.user' 2>/dev/null; then
        echo "Deployed: ✓ solver.web.user importable from ${VENV_DIR}"
    else
        echo "Deployed: … solver.web.user not in the venv yet (step 4) — unit deferred"
    fi
}

# The public GitHub URL every per-user clone is taken from — read straight off the
# operator repo's origin remote, so there is one source of truth and no hard-coding.
origin_url() { git -C "${PROJECT_ROOT}" remote get-url origin 2>/dev/null; }

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
Documentation=https://github.com/vikasmunshi/euler/blob/master/docs/web-server-guide.md

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
Documentation=https://github.com/vikasmunshi/euler/blob/master/docs/web-server-guide.md
After=network.target euler-auth.service
Wants=euler-auth.service
Requires=euler-user@%i.socket

[Service]
# Type=simple, like every sibling kit: the app never sd_notify()s, so Type=notify
# would leave systemd waiting for a READY=1 that never comes — it then declares the
# start "timed out" at TimeoutStartSec (90s), SIGTERMs the WHOLE cgroup (killing the
# user's live PTY shell), and Restart= respawns it: an endless ~95s reset loop. The
# .socket unit is the real readiness gate anyway — it queues connections until the
# listener is up.
Type=simple
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

# Run a provisioning step AS the collaborator's own uid (never root): a heredoc
# script under `sudo -Hu`, so every file it creates is born with the right owner —
# no chown sweep, and no window where root-owned files sit in a user's home. The
# euler-user-* uids are inside the egress lock (firewall.sh), so the script first
# sources /etc/euler/egress.env: outbound HTTP(S) goes through Squid or not at all
# (root, by contrast, bypassed the lock — one more reason not to work as root).
as_user() {
    local user="$1"; shift
    sudo -Hu "${user}" env "$@" EGRESS_ENV="${EGRESS_ENV}" bash -s
}

# Clone the repo into ~/euler on branch user/<slug>, filter DISABLED → ciphertext at
# rest. Clone straight from the public GitHub repo: GitHub stores only the filter's
# ciphertext (the clean output), anonymous read needs no credentials, and origin stays
# the GitHub URL so the user can push user/<slug> as themselves later (MT-2). Runs AS
# the user; github.com is in the Squid allowlist, so the clone rides the proxy.
provision_clone() {
    local slug="$1" user home clone url
    user="$(user_of "${slug}")"
    home="$(home_of "${slug}")"
    clone="${home}/euler"
    if [ -d "${clone}/.git" ]; then
        # A repair-run keeps the clone but re-renders the hooks: the templates evolve
        # (new gates), and the hooks live in .git/hooks — untracked, so nothing else
        # refreshes them. githooks.sh install is idempotent and --force skips the
        # backup rotation (the rendered copies carry no local edits by contract).
        echo "Clone ${clone} already present — re-rendering the git hooks (venv ${VENV_DIR})..."
        as_user "${user}" EULER_VENV="${VENV_DIR}" <<'HOOKS'
set -euo pipefail
bash "${HOME}/euler/scripts/setup/githooks.sh" install --force
HOOKS
        return 0
    fi
    url="$(origin_url)"
    if [ -z "${url}" ]; then
        echo "Error: could not read the origin URL from ${PROJECT_ROOT} — is it a checkout?" >&2
        return 1
    fi
    echo "Cloning ${url} into ${clone} as ${user} (filter disabled → ciphertext at rest)..."
    # No filter is wired in the clone's local config, and .gitattributes' rule is not
    # 'required', so solutions/private/** checks out as the ciphertext GitHub holds.
    # Commit authorship + push credential are the user's own (MT-2), configured
    # self-service in their shell later (`git-identity`). The git hooks (pre-commit
    # flake8+mypy + the gitfilter gate, pre-push) render into .git/hooks — not tracked,
    # so a clone lands without them — pointed at the deployed /opt/euler venv since a
    # per-user clone has no .venv.
    as_user "${user}" URL="${url}" SLUG="${slug}" EULER_VENV="${VENV_DIR}" <<'CLONE'
set -euo pipefail
[ -f "${EGRESS_ENV}" ] && { set -a; . "${EGRESS_ENV}"; set +a; }
git clone --branch master "${URL}" "${HOME}/euler"
git -C "${HOME}/euler" checkout -B "user/${SLUG}"
echo "Installing git hooks (venv ${EULER_VENV})..."
bash "${HOME}/euler/scripts/setup/githooks.sh" install --force
CLONE
}

# Install the Claude Code CLI into the user's own home (~/.local/bin) — their login,
# their config, their spend (MT-6): the `claude` binary is per-user by design, exactly
# like their vault. Runs the CLONE's own claude_code.sh AS the user, so its project
# links land in their clone; best-effort — the download rides Squid, so downloads.claude.ai
# (and claude.ai / code.claude.com) must be in the egress allowlist or this skips with
# a warning and the user is told how to finish later.
provision_claude() {
    local slug="$1" user home
    user="$(user_of "${slug}")"
    home="$(home_of "${slug}")"
    if [ ! -x "${home}/euler/scripts/setup/claude_code.sh" ]; then
        echo "note: no claude_code.sh in the clone — skipping the Claude Code install."
        return 0
    fi
    echo "Installing Claude Code for ${user} (via Squid)..."
    if ! as_user "${user}" <<'CLAUDE'
set -euo pipefail
[ -f "${EGRESS_ENV}" ] && { set -a; . "${EGRESS_ENV}"; set +a; }
bash "${HOME}/euler/scripts/setup/claude_code.sh" install
CLAUDE
    then
        echo "warn: Claude Code install failed — likely the egress allowlist (needs .claude.ai,"
        echo "      code.claude.com; edit /etc/euler-proxy/squid.allowlist + 'egress.sh reload')."
        echo "      The user can finish later in their shell: ! bash scripts/setup/claude_code.sh install"
    fi
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
    ensure_user_identity "${slug}"
    provision_clone "${slug}"
    provision_claude "${slug}"
    enable_socket "${slug}"
    # The new uid must be inside the egress lock, or (chain policy accept) it would reach
    # the internet directly, bypassing Squid. firewall.sh enumerates euler-user-* by group.
    if [ -f /etc/systemd/system/euler-firewall.service ]; then
        echo "Reloading the egress firewall to cover $(user_of "${slug}")..."
        "${SCRIPT_DIR}/firewall.sh" reload || echo "warn: firewall reload failed — run 'make upgrade-firewall'"
    fi
    echo "Provisioned ${slug}${email:+ (}${email}${email:+)} → profile ${profile}."
    echo "Next (self-service, in the user's web shell): \`git-identity\` (GitHub sign-in +"
    echo "commit authorship), generate a key (\`user\`), have an admin \`user-authorize\` it"
    echo "+ push, then \`git-sync\` — the pull wires the filter and decrypts their private tree."
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
    echo "Refreshed ${USER_ENV}."
    # Pick up a freshly rebuilt /opt/euler venv (redeploy-auth): stop each running
    # instance — this drops that user's live shell — and leave its socket listening,
    # so the next request re-activates the service against the new code.
    local users u slug
    users="$(getent passwd | awk -F: '/^euler-user-/{print $1}' || true)"
    for u in ${users}; do
        slug="${u#euler-user-}"
        if systemctl is-active --quiet "euler-user@${slug}.service" 2>/dev/null; then
            echo "Stopping euler-user@${slug}.service (its socket re-activates it on the next request)..."
            sudo systemctl stop "euler-user@${slug}.service"
        fi
    done
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

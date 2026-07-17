#!/usr/bin/env bash
# Per-user provisioning kit (euler-user) — step 3 of the multi-tenant redesign
# ==============================================================================
#
# Deploys / removes the OS layer for the **per-user** web tier, and provisions
# or tears down one collaborator at a time. This replaces the per-*profile*
# shared-uid model: instead of three fixed rungs sharing a uid, every
# collaborator gets their **own** uid, home, and repo clone, so their
# own keys can rest in their own uid-private home without leaking to anyone else.
# Design of record: docs/web-server-guide.md § The per-user tier.
#
# Two planes:
#
#   deploy / remove / status  — the SHARED layer, once per host:
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
# requires sudo.
#
# Actions: deploy | remove | upgrade | redeploy | provision | deprovision | status | help
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

# The system venv — OPT_DIR / VENV_DIR / VENV_PY / PYTHON / deploy_venv.
# shellcheck source=scripts/setup/venv.sh
. "${SCRIPT_DIR}/venv.sh"

usage() {
    cat <<USAGE
Usage: $0 <action> [args]

  deploy                       Create the euler-user group, /etc/euler/user.env, and —
                               when solver.web.user is in the /opt/euler venv — the
                               euler-user@.service/.socket template. Idempotent.
  remove                       Remove the template + user.env (prompted). Provisioned
                               users must be deprovisioned first.
  upgrade                      Alias of deploy: re-assert the shared layer.
  redeploy                     Refresh /etc/euler/user.env, re-lay every provisioned
                               user's git hooks from this repo, and stop the running
                               instances so their sockets re-activate them against a
                               freshly rebuilt venv (drops live shells).
  provision <slug> <email> <profile>
                               Provision one collaborator: uid + home (0700), a
                               filter-disabled clone of ~/euler from the public GitHub
                               repo on branch user/<slug> (cloned AS the user, through
                               Squid), git hooks rendered from THIS repo's templates,
                               Claude Code (~/.local/bin, theirs), ~/.euler, and the
                               instance socket. Idempotent — re-run it to repair an
                               instance and re-lay its hooks; the clone is left as it
                               stands (this plane cannot sync it).
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
# letter-led, [a-z0-9-] only. Refuse anything else — this value becomes a uid,
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
# key: each user brings their own, in their own vault. The per-instance
# EULER_REPO_ROOT / EULER_USER_SLUG / socket come from the template unit (%i).
deploy_user_env() {
    sudo mkdir -p "${SYS_DIR}"
    sudo tee "${USER_ENV}" > /dev/null <<EOF
# GENERATED by scripts/setup/user.sh — scoped runtime config for euler-user.
# The per-instance EULER_REPO_ROOT, EULER_USER_SLUG and socket are set by the unit (%i).
# No credentials here, deliberately: each user's secrets live in their own vault,
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
# Caddy dials by the forward_auth X-User-Slug. Serves BOTH the content
# routes and /ws — one service, not the retired content@/ws@ split.
install_units() {
    echo "Installing ${SOCKET_TEMPLATE} + ${SERVICE_TEMPLATE} (socket-activated, per-user)..."
    sudo tee "${SOCKET_DEST}" > /dev/null <<EOF
[Unit]
Description=euler per-user instance socket (%i) — the collaborator's content + /ws
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
Description=euler per-user instance (%i) — one collaborator's content + web shell
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
# HTTPS_PROXY: the problem scraper egresses only through Squid.
EnvironmentFile=-${EGRESS_ENV}
Environment=EULER_USER_SLUG=%i
Environment=EULER_REPO_ROOT=${USER_HOME_BASE}/euler-user-%i/euler
ExecStart=${VENV_PY} -m solver.web.user
Restart=on-failure
RestartSec=5s

# Egress layer 1: loopback only — the /run/euler sockets and the Squid proxy. The kernel
# firewall (firewall.sh, scoped to the euler-user-* uids) is layer 2.
IPAddressDeny=any
IPAddressAllow=localhost

# Hardening. This tier runs the user's own code by design, contained to
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

# Lay the git hooks into a provisioned clone, rendered from THIS repo's templates.
#
# The operator checkout is the source: the hooks a collaborator runs must be the ones this
# repo ships, never whatever their clone happens to hold. A clone can sit behind master
# indefinitely and nothing on this plane can move it forward — a sync would check out
# solutions/private through the smudge filter, whose master key lives in the user's own
# vault, locked to their session and deliberately unreachable from root. So the clone's own
# templates are not a source this plane can trust, and the hooks are copied in from here.
#
# Rendered by substituting the deployed venv for __VENV__: a per-user clone has no .venv, so
# its hooks' flake8/mypy must call /opt/euler/venv. That is the only substitution the
# templates take — they resolve REPO_ROOT at runtime (git rev-parse), so one rendered file
# is correct in any checkout, which is what makes copying them in sound at all.
#
# Rendered as the operator and installed by root, because this is the one provisioning step
# whose source sits in the operator's 0750 home: the euler-user uids cannot read it, so
# as_user has nothing to read and root must place the file. `install` sets the owner as it
# copies, so the hook is never a root-owned file in the user's home, not even briefly.
provision_hooks() {
    local slug="$1" user clone hook src rendered
    user="$(user_of "${slug}")"
    clone="$(home_of "${slug}")/euler"
    if ! sudo test -d "${clone}/.git"; then
        echo "note: no clone at ${clone} — skipping the git hooks."
        return 0
    fi
    echo "Installing the git hooks from ${PROJECT_ROOT} into ${clone} (venv ${VENV_DIR})..."
    for hook in pre-commit pre-push; do
        src="${PROJECT_ROOT}/scripts/setup/hooks/${hook}.template"
        if [ ! -f "${src}" ]; then
            echo "warn: ${src} not found — skipping the ${hook} hook." >&2
            continue
        fi
        rendered="$(mktemp)"
        sed -e "s|__VENV__|${VENV_DIR}|g" -e "s|__REPO_ROOT__|${clone}|g" "${src}" > "${rendered}"
        sudo install -o "${user}" -g "${user}" -m 0755 "${rendered}" "${clone}/.git/hooks/${hook}"
        rm -f "${rendered}"
        echo "Installed hook: ${hook}"
    done
}

# Clone the repo into ~/euler on branch user/<slug>, filter DISABLED → ciphertext at
# rest. Clone straight from the public GitHub repo: GitHub stores only the filter's
# ciphertext (the clean output), anonymous read needs no credentials, and origin stays
# the GitHub URL so the user can push user/<slug> as themselves later. Runs AS
# the user; github.com is in the Squid allowlist, so the clone rides the proxy.
provision_clone() {
    local slug="$1" user home clone url
    user="$(user_of "${slug}")"
    home="$(home_of "${slug}")"
    clone="${home}/euler"
    # A repair-run keeps the clone exactly as it stands: this plane cannot move it forward
    # (see provision_hooks), so there is nothing to do here but leave it be. do_provision
    # re-lays the hooks either way — that, not the clone, is what a repair refreshes.
    if sudo test -d "${clone}/.git"; then
        echo "Clone ${clone} already present — leaving it as it stands."
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
    # Commit authorship + push credential are the user's own, configured
    # self-service in their shell later (`git-identity`). The hooks are not laid here:
    # they come from the operator checkout, in provision_hooks, for a fresh clone and a
    # repair alike — one source, so a clone can never render its own.
    as_user "${user}" URL="${url}" SLUG="${slug}" <<'CLONE'
set -euo pipefail
[ -f "${EGRESS_ENV}" ] && { set -a; . "${EGRESS_ENV}"; set +a; }
git clone --branch master "${URL}" "${HOME}/euler"
git -C "${HOME}/euler" checkout -B "user/${SLUG}"
CLONE
}

# Install the Claude Code CLI into the user's own home (~/.local/bin) — their login,
# their config, their spend: the `claude` binary is per-user by design, exactly
# like their vault. Runs the CLONE's own claude_code.sh AS the user, so its project
# links land in their clone; best-effort — the download rides Squid, so downloads.claude.ai
# (and claude.ai / code.claude.com) must be in the egress allowlist or this skips with
# a warning and the user is told how to finish later.
provision_claude() {
    local slug="$1" user home
    user="$(user_of "${slug}")"
    home="$(home_of "${slug}")"
    if ! sudo test -x "${home}/euler/scripts/setup/claude_code.sh"; then
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
    provision_hooks "${slug}"
    provision_claude "${slug}"
    enable_socket "${slug}"
    # The new uid must be inside the egress lock, or (chain policy accept) it would reach
    # the internet directly, bypassing Squid. firewall.sh enumerates euler-user-* by group.
    if [ -f /etc/systemd/system/euler-firewall.service ]; then
        echo "Reloading the egress firewall to cover $(user_of "${slug}")..."
        "${SCRIPT_DIR}/firewall.sh" reload || echo "warn: firewall reload failed — run 'make deploy-firewall'"
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

do_deploy() {
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
    # Pick up a freshly rebuilt /opt/euler venv (redeploy-auth): re-lay each user's hooks
    # from this repo, then stop each running instance — this drops that user's live shell —
    # and leave its socket listening, so the next request re-activates the service against
    # the new code.
    #
    # The hooks belong in redeploy for the same reason the venv does: they are the
    # operator's code running in the user's clone, they bake the deployed venv's path, and
    # a clone cannot refresh them itself. This is the one sweep that reaches every
    # provisioned user, so it is where a template change (a new gate) actually lands for
    # everyone — otherwise a hook fix would only reach a user who happened to be
    # reprovisioned.
    local users u slug
    users="$(getent passwd | awk -F: '/^euler-user-/{print $1}' || true)"
    for u in ${users}; do
        slug="${u#euler-user-}"
        provision_hooks "${slug}"
        if systemctl is-active --quiet "euler-user@${slug}.service" 2>/dev/null; then
            echo "Stopping euler-user@${slug}.service (its socket re-activates it on the next request)..."
            sudo systemctl stop "euler-user@${slug}.service"
        fi
    done
    do_status
}

do_remove() {
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

# One marker vocabulary for every status line, shared layer and per-user alike:
#
#   ✓ present / healthy
#   ✗ missing / broken        — always a fault, always worth acting on
#   … deferred                — a legitimate not-yet (a later step lays it down), not a fault
#
# Every field leads with its marker, so a fault reads the same way wherever it appears.
# The per-user line used to spell its faults in prose ("no-clone") between two ✓s, where
# they went unread for weeks — hence: no word carries a verdict that a marker doesn't.
OK='✓'
BAD='✗'
DEFER='…'

# "label:       <mark> <detail>" — the shared-layer column.
status_line() { printf '%-12s %s %s\n' "$1:" "$2" "$3"; }

# Echo ✓ if the check succeeds, ✗ if it fails. Written as if/else rather than
# `cmd && echo ✓ || echo ✗` so `set -e` never sees a bare failing command, and so a
# check that fails cannot be mistaken for one that printed nothing.
check_mark() {
    if "$@" > /dev/null 2>&1; then printf '%s' "${OK}"; else printf '%s' "${BAD}"; fi
}

do_status() {
    if [ ! -x "${VENV_PY}" ]; then
        status_line "venv" "${BAD}" "${VENV_DIR} not deployed (run auth.sh / user.sh deploy)"
    elif "${VENV_PY}" -P -c 'import solver.web.user' 2>/dev/null; then
        status_line "venv" "${OK}" "solver.web.user importable from ${VENV_DIR}"
    else
        status_line "venv" "${DEFER}" "solver.web.user not in the venv yet (step 4)"
    fi
    status_line "group" "$(check_mark getent group "${USER_GROUP}")" "${USER_GROUP}"
    status_line "config" "$(check_mark test -f "${USER_ENV}")" "${USER_ENV}"
    if [ -f "${SOCKET_DEST}" ]; then
        status_line "template" "${OK}" "${SOCKET_TEMPLATE} + ${SERVICE_TEMPLATE}"
    else
        status_line "template" "${DEFER}" "deferred (solver.web.user not yet deployed)"
    fi

    # Per-user roster (or one slug's instance).
    local slug="${1:-}"
    if [ -n "${slug}" ]; then
        status_line "users" "${OK}" "1 requested"
        status_one "${slug}"
        return 0
    fi
    local users u
    users="$(getent passwd | awk -F: '/^euler-user-/{print $1}' || true)"
    if [ -z "${users}" ]; then
        status_line "users" "${DEFER}" "none provisioned"
        return 0
    fi
    status_line "users" "${OK}" "$(wc -l <<< "${users}") provisioned"
    for u in ${users}; do
        status_one "${u#euler-user-}"
    done
}

# One indented line per collaborator, every field marked. The slug column is fixed at 20 —
# valid_slug's own ceiling — so the fields line up and a ✗ sits in a column you can scan.
status_one() {
    local slug="$1" user home clone socket
    user="$(user_of "${slug}")"
    home="$(home_of "${slug}")"
    clone="${home}/euler"
    if ! getent passwd "${user}" > /dev/null 2>&1; then
        printf '  %-20s %s %s missing\n' "${slug}" "${BAD}" "${user}"
        return 0
    fi
    if [ ! -f "${SOCKET_DEST}" ]; then
        socket="${DEFER} deferred"
    elif systemctl is-active --quiet "euler-user@${slug}.socket" 2>/dev/null; then
        socket="${OK} active"
    else
        socket="${BAD} inactive"
    fi
    # The clone and its hooks live under a 0700 home — only root can see them (as vikas the
    # test silently reads "absent", which is exactly how "no-clone" got misreported).
    printf '  %-20s uid %s · clone %s · hooks %s · socket %s\n' \
        "${slug}" \
        "${OK}" \
        "$(check_mark sudo test -d "${clone}/.git")" \
        "$(check_mark sudo test -x "${clone}/.git/hooks/pre-commit" -a -x "${clone}/.git/hooks/pre-push")" \
        "${socket}"
}

# ── Dispatch ──────────────────────────────────────────────────────────────────────────
ACTION="${1:-status}"
shift || true
case "${ACTION}" in
    deploy)      do_deploy ;;
    upgrade)     do_deploy ;;
    redeploy)    do_redeploy ;;
    remove)      do_remove ;;
    provision)   do_provision "$@" ;;
    deprovision) do_deprovision "$@" ;;
    status)      do_status "$@" ;;
    -h | --help | help) usage ;;
    *) echo "Unknown action: ${ACTION}"; usage; exit 1 ;;
esac

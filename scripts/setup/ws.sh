#!/usr/bin/env bash
# Web-shell service kit (euler-ws) — Phase 6 of the server redesign (DD-13/DD-14)
# ==============================================================================
#
# Installs / uninstalls / upgrades the OS layer for the **web shell**: the
# per-profile service identities, the systemd template unit `euler-ws@<profile>`
# (one instance per web profile), and the shell-state ACLs — all running from the
# shared root-owned /opt/euler system venv (DD-5). Sibling to content.sh, whose
# shape it deliberately mirrors; see docs/secure-web-server.md (DD-13/DD-14).
#
# This is the highest-risk service in the stack: a web shell is arbitrary code
# execution as its uid, by design (security-notes AR-1). What contains it:
#
#   - **Per-profile uids (DD-13).** euler-ws@{reader,contributor,maintainer}, each
#     `User=euler-ws-<profile>` on its own socket /run/euler/ws-<profile>.sock, and
#     Caddy routes by the X-Profile that forward_auth returns (frontend.sh). Each
#     instance is *born* as the right uid — no setuid, no root. The app pins
#     EULER_PROFILE=%i and refuses a mismatched X-Profile, and the forked shell
#     aborts if its redeemed ticket's profile differs from the pin.
#   - **Every rung gets a terminal** (attach = `solver:execute`, the reader floor):
#     what differs is the command set the shell registers, which the DD-12 decorator
#     decides — a reader shell has no eval/benchmark/edit and no shell escape.
#   - **The same content-tree ACLs as the content tier** (no new object paths): all
#     three in euler-sol-read; contributor+ also euler-sol-write; maintainer also
#     euler-sol-delete. `.git`, `keys/`, and the solver source stay out of the ACL
#     set — the master key never reaches the web tier (AR-2).
#   - **One addition the content tier never needed:** `.state/` (per-user shell
#     history / last problem / session log). All three uids need it read-write —
#     even a reader's shell keeps history — so it gets its own group.
#   - **Loopback-only egress (DD-8)**: IPAddressDeny=any + IPAddressAllow=localhost,
#     and HTTPS_PROXY from /etc/euler/egress.env, so the problem scraper reaches
#     projecteuler.net through Squid and nothing else leaves.
#   - **No credentials.** No API key is deployed to any ws uid: the AI commands
#     register for a maintainer but fail with a clear no-credentials error until the
#     Phase-7 `euler-ai` broker exists (DD-15).
#
#   /opt/euler/venv                        root:euler-web 0755  (shared venv, DD-5)
#   /etc/euler/ws.env                      root:euler-web 0640  (generated here)
#   /etc/systemd/system/euler-ws@.service  (root-owned template; one instance per
#                                           web profile; deferred until solver.web.ws
#                                           exists in the venv)
#
# Because the units live in root's systemd and run as locked-down users, lifecycle
# (start/stop/restart) requires sudo (DD-3).
#
# Actions: install | uninstall | upgrade | redeploy | status | help
#
# Author: Vikas Munshi <vikas.munshi@gmail.com>
# Copyright (c) 2026. All rights reserved.
# Licensed under the MIT License.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
HOME_DIR="$(dirname "${PROJECT_ROOT}")"                 # the operator home the repo lives in

SYS_DIR="/etc/euler"
WS_ENV="${SYS_DIR}/ws.env"                              # scoped runtime config (root:euler-web 0640)
EGRESS_ENV="${SYS_DIR}/egress.env"                      # HTTPS_PROXY (egress.sh)
OPT_DIR="/opt/euler"
VENV_DIR="${OPT_DIR}/venv"
VENV_PY="${VENV_DIR}/bin/python"

PYTHON="python3.14"                                     # the project floor; deadsnakes on 24.04

WEB_GROUP="euler-web"
# The web profiles that get an instance (admin is local-only; web caps at maintainer, DD-11).
# Every one of them gets a terminal — attach is `solver:execute`, a reader grant (DD-13).
PROFILES=(reader contributor maintainer)
# Content-tree ACL groups — **created and ACL'd by content.sh**; the ws uids simply join
# them, so the two tiers can never diverge on what the filesystem allows.
SOL_READ_GROUP="euler-sol-read"
SOL_WRITE_GROUP="euler-sol-write"
SOL_DELETE_GROUP="euler-sol-delete"
# The shell-state group: `.state/<slug>/` (history, last problem, session log). Owned here
# — the content service has no shell and never needed it.
STATE_GROUP="euler-ws-state"
STATE_DIR="${PROJECT_ROOT}/.state"

SERVICE_TEMPLATE="euler-ws@.service"
SERVICE_DEST="/etc/systemd/system/${SERVICE_TEMPLATE}"

usage() {
    cat <<USAGE
Usage: $0 [install|uninstall|upgrade|redeploy|status|help]

  install    Create the per-profile euler-ws-<profile> identities (joining the
             euler-sol-* groups content.sh owns) and the euler-ws-state group,
             apply the .state/ ACLs, deploy /etc/euler/ws.env, and — when
             solver.web.ws exists in the /opt/euler venv — install the root-owned
             euler-ws@.service template and enable an instance per web profile.
  uninstall  Disable the instances, remove the unit + ws.env, strip the .state
             ACLs, and (prompted) remove the identities/group.
  upgrade    Re-assert identities, ACLs, config, and units; restart the instances.
  redeploy   Fast path: refresh /etc/euler/ws.env and restart the instances to pick
             up new code — no identities, ACLs, or unit changes. (The shared
             /opt/euler venv is rebuilt by 'auth.sh redeploy'.)
  status     Show venv/deps, identities, ACLs, config, and instance health.

  Requires: the /opt/euler venv (auth.sh) and the content-tree ACL groups (content.sh).
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
        echo "Error: systemd is required for the web-shell service; it is not active here." >&2
        return 1
    fi
}

require_python() {
    if ! command -v "${PYTHON}" &> /dev/null; then
        echo "Error: ${PYTHON} not found — run 'make install-system' (deadsnakes) first." >&2
        return 1
    fi
}

require_acl() {
    if command -v setfacl &> /dev/null; then
        return 0
    fi
    echo "Installing the acl package (setfacl) for the .state ACLs..."
    sudo apt-get install -y acl
}

# The content-tree ACL groups belong to content.sh (it creates them *and* applies the
# subtree ACLs from authorizations.json). The ws uids only join them — so refuse to run
# before the content kit has, rather than half-creating a group whose ACLs nobody applied.
require_sol_groups() {
    local grp missing=()
    for grp in "${SOL_READ_GROUP}" "${SOL_WRITE_GROUP}" "${SOL_DELETE_GROUP}"; do
        getent group "${grp}" > /dev/null || missing+=("${grp}")
    done
    if [ ${#missing[@]} -gt 0 ]; then
        echo "Error: missing content-tree ACL groups: ${missing[*]}" >&2
        echo "       Run 'make install-content' first — content.sh owns those groups and the" >&2
        echo "       subtree ACLs they carry; ws.sh only adds its uids to them." >&2
        return 1
    fi
}

# Create the per-profile shell identities (idempotent). Group membership mirrors the
# content tier's exactly — the same rung reaches the same files through either service —
# plus the shell-state group every rung needs.
ensure_identities() {
    getent group "${WEB_GROUP}"  > /dev/null || sudo groupadd --system "${WEB_GROUP}"
    getent group "${STATE_GROUP}" > /dev/null || sudo groupadd --system "${STATE_GROUP}"

    local profile user own_group extra
    for profile in "${PROFILES[@]}"; do
        user="euler-ws-${profile}"
        own_group="${user}"
        case "${profile}" in
            reader)      extra="${WEB_GROUP},${STATE_GROUP},${SOL_READ_GROUP}" ;;
            contributor) extra="${WEB_GROUP},${STATE_GROUP},${SOL_READ_GROUP},${SOL_WRITE_GROUP}" ;;
            maintainer)  extra="${WEB_GROUP},${STATE_GROUP},${SOL_READ_GROUP},${SOL_WRITE_GROUP},${SOL_DELETE_GROUP}" ;;
            *)           extra="${WEB_GROUP},${STATE_GROUP},${SOL_READ_GROUP}" ;;
        esac
        getent group "${own_group}" > /dev/null || sudo groupadd --system "${own_group}"
        if ! getent passwd "${user}" > /dev/null; then
            echo "Creating system user ${user} (group ${own_group}, +${extra})..."
            sudo useradd --system --no-create-home --shell /usr/sbin/nologin \
                -g "${own_group}" -G "${extra}" "${user}"
        else
            sudo usermod -g "${own_group}" -G "${extra}" "${user}"      # re-assert exact membership
        fi
    done
}

# Build/refresh the shared /opt/euler venv and (re)install the repo so the DEPLOYED
# package matches the source — the units run `-m solver.web.ws` from it (cwd=/, so a
# stale venv fails even when the repo has the module). Idempotent with auth.sh/content.sh.
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
    # -P: ignore cwd, so this probes the venv's copy (not the repo we're standing in).
    if sudo "${VENV_PY}" -P -c 'import solver.web.ws' 2>/dev/null; then
        echo "Deployed: ✓ solver.web.ws importable from ${VENV_DIR}"
    else
        echo "Deployed: ✗ solver.web.ws NOT importable from the venv" >&2
    fi
}

# Scoped runtime config for the ws instances (never the full ~/.euler/env, and no API
# key — DD-13/DD-15). The per-instance EULER_PROFILE / EULER_WS_SOCKET come from the
# template unit (%i).
deploy_ws_env() {
    sudo mkdir -p "${SYS_DIR}"
    sudo tee "${WS_ENV}" > /dev/null <<EOF
# GENERATED by scripts/setup/ws.sh — scoped runtime config for euler-ws (DD-13).
# The per-instance EULER_PROFILE and EULER_WS_SOCKET are set by the template unit.
# No ANTHROPIC_API_KEY here, deliberately: no credential reaches an RCE-by-design uid.
# The AI commands register for a maintainer and fail with a clear no-credentials
# error until the Phase-7 euler-ai broker (DD-15) serves them.
EULER_REPO_ROOT=${PROJECT_ROOT}
EULER_WEB_GROUP=${WEB_GROUP}
EULER_AUTH_SOCKET=/run/euler/auth.sock
EULER_WS_DETACHED_TTL=86400
EOF
    sudo chown root:"${WEB_GROUP}" "${WS_ENV}"
    sudo chmod 0640 "${WS_ENV}"
}

# The shell-state ACLs. `.state/<slug>/` holds each web user's shell history, last
# problem, and session log; every rung's shell writes it (a reader has history too), so
# all three uids get rwX through one group — recursive + default, so directories the
# shell creates inherit it. The content tree's ACLs are content.sh's (the ws uids reach
# it through the euler-sol-* groups they joined above).
deploy_acls() {
    require_acl
    mkdir -p "${STATE_DIR}"
    echo "Applying shell-state ACLs (${STATE_GROUP}:rwX on ${STATE_DIR})..."
    # Traverse the home path + repo root (idempotent with content.sh's identical grant).
    sudo setfacl -m "g:${WEB_GROUP}:x" "${HOME_DIR}" "${PROJECT_ROOT}"
    sudo setfacl -R  -m "g:${STATE_GROUP}:rwX" "${STATE_DIR}"
    sudo setfacl -R -d -m "g:${STATE_GROUP}:rwX" "${STATE_DIR}"
}

strip_acls() {
    command -v setfacl &> /dev/null || return 0
    echo "Stripping shell-state ACLs..."
    if [ -d "${STATE_DIR}" ]; then
        sudo setfacl -R  -x "g:${STATE_GROUP}" "${STATE_DIR}" 2>/dev/null || true
        sudo setfacl -R -d -x "g:${STATE_GROUP}" "${STATE_DIR}" 2>/dev/null || true
    fi
}

# True when the deployed venv carries the web-shell module (build-order gate).
venv_has_ws() {
    [ -x "${VENV_PY}" ] && sudo "${VENV_PY}" -P -c 'import solver.web.ws' 2>/dev/null
}

install_units() {
    echo "Installing ${SERVICE_TEMPLATE} (per-profile, loopback-only)..."
    sudo tee "${SERVICE_DEST}" > /dev/null <<EOF
[Unit]
Description=euler web shell (%i) — the solver PTY terminal over WebSocket (Phase 6, DD-13)
Documentation=https://github.com/vikasmunshi/euler/blob/master/docs/secure-web-server.md
After=network.target euler-auth.service
Wants=euler-auth.service

[Service]
Type=simple
# Born as the per-profile uid — no setuid, no root. systemd loads the uid's full group
# list (euler-web + euler-ws-state + the euler-sol-* it is entitled to) from the user
# database, so the filesystem tells the rungs apart even though the app also gates them.
User=euler-ws-%i
EnvironmentFile=${WS_ENV}
# HTTPS_PROXY: the problem scraper egresses only through Squid (DD-8/Phase 2).
EnvironmentFile=-${EGRESS_ENV}
Environment=EULER_PROFILE=%i
Environment=EULER_WS_SOCKET=/run/euler/ws-%i.sock
ExecStart=${VENV_PY} -m solver.web.ws
Restart=on-failure
RestartSec=5s

# DD-8 layer 1: loopback only — the /run/euler sockets (Caddy, the auth ticket plane)
# and the Squid proxy. The kernel firewall (firewall.sh) is layer 2.
IPAddressDeny=any
IPAddressAllow=localhost

# Hardening. This service runs arbitrary user code by design (AR-1), so the containment
# that matters is the uid + the ACLs + the egress lock, not a syscall sandbox — and the
# sandbox must not break the thing being run:
#   ProtectHome=false        — the shell reads the repo working tree under the operator
#                              home; the content-tree ACLs (not the sandbox) confine it.
#   ReadWritePaths           — the sockets, the solutions tree (results/benchmarks), and
#                              .state (per-user shell state). Everything else read-only.
#   MemoryDenyWriteExecute   — deliberately NOT set: solutions may legitimately need
#                              W^X-violating runtimes (native extensions), and denying it
#                              would break `evaluate` while buying little against a tier
#                              that already runs the user's own code.
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=false
ReadWritePaths=/run/euler ${PROJECT_ROOT}/solutions ${STATE_DIR}
PrivateTmp=true
PrivateDevices=true
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
CapabilityBoundingSet=
LockPersonality=true
RestrictRealtime=true
SystemCallArchitectures=native
UMask=0007

# One PTY child per attached user; systemd's cgroup kill collects them all on stop, so
# no shell survives the service (DD-14's last teardown path).
KillMode=control-group
TimeoutStopSec=20s

[Install]
WantedBy=multi-user.target
EOF
    sudo systemctl daemon-reload
    restart_instances
}

restart_instances() {
    local profile
    for profile in "${PROFILES[@]}"; do
        sudo systemctl enable --now "euler-ws@${profile}.service"
        sudo systemctl restart "euler-ws@${profile}.service"
    done
}

# ── install / uninstall ───────────────────────────────────────────────────────────

do_install() {
    check_can_sudo || return 1
    require_systemd || return 1
    require_python || return 1
    require_sol_groups || return 1
    ensure_identities
    deploy_venv
    deploy_ws_env
    deploy_acls

    if venv_has_ws; then
        install_units
    else
        echo "note: solver.web.ws not yet in the deployed package — instances deferred"
        echo "      (re-run '$0 upgrade' once the venv carries it)."
    fi

    # The per-profile uids are part of the nftables egress ruleset — regenerate.
    if [ -f /etc/systemd/system/euler-firewall.service ]; then
        echo "Reloading the egress firewall to include the euler-ws-* uids..."
        "${SCRIPT_DIR}/firewall.sh" reload
    fi
    # Caddy routes /ws by X-Profile to these sockets — regenerate the Caddyfile.
    echo "Refreshing the edge so /ws routes to the per-profile sockets..."
    "${SCRIPT_DIR}/frontend.sh" redeploy
    do_status
}

do_redeploy() {
    check_can_sudo || return 1
    require_systemd || return 1
    deploy_ws_env
    if [ -f "${SERVICE_DEST}" ] && venv_has_ws; then
        restart_instances
        echo "Restarted the per-profile web-shell instances (live shells are dropped)."
    else
        echo "note: web-shell instances not installed yet — run '$0 install'."
    fi
    do_status
}

do_uninstall() {
    check_can_sudo || return 1
    if [ -f "${SERVICE_DEST}" ]; then
        local profile
        for profile in "${PROFILES[@]}"; do
            sudo systemctl disable --now "euler-ws@${profile}.service" 2>/dev/null || true
        done
        sudo rm -f "${SERVICE_DEST}"
        sudo systemctl daemon-reload
    fi
    sudo rm -f "${WS_ENV}"

    local reply
    read -r -p "Strip the .state ACLs from ${STATE_DIR}? [y/N] " reply
    [[ "${reply}" =~ ^[Yy]$ ]] && strip_acls

    read -r -p "Remove the euler-ws-* identities and the ${STATE_GROUP} group? [y/N] " reply
    if [[ "${reply}" =~ ^[Yy]$ ]]; then
        local profile user
        for profile in "${PROFILES[@]}"; do
            user="euler-ws-${profile}"
            getent passwd "${user}" > /dev/null && sudo userdel "${user}" 2>/dev/null || true
            getent group  "${user}" > /dev/null && sudo groupdel "${user}" 2>/dev/null || true
        done
        getent group "${STATE_GROUP}" > /dev/null && sudo groupdel "${STATE_GROUP}" 2>/dev/null || true
    fi
    echo "Web-shell service uninstall complete."
}

# ── status ────────────────────────────────────────────────────────────────────────

do_status() {
    if [ -x "${VENV_PY}" ]; then
        if "${VENV_PY}" -P -c 'import solver.web.ws' 2>/dev/null; then
            echo "venv:        ✓ solver.web.ws importable from ${VENV_DIR}"
        else
            echo "venv:        ✗ solver.web.ws not importable from the venv"
        fi
    else
        echo "venv:        ✗ ${VENV_DIR} not deployed (run auth.sh / ws.sh install)"
    fi
    local profile user
    for profile in "${PROFILES[@]}"; do
        user="euler-ws-${profile}"
        if getent passwd "${user}" > /dev/null; then
            echo "identity:    ✓ ${user} (groups: $(id -nG "${user}" 2>/dev/null))"
        else
            echo "identity:    ✗ ${user} missing"
        fi
    done
    getent group "${STATE_GROUP}" > /dev/null \
        && echo "state group: ✓ ${STATE_GROUP}" || echo "state group: ✗ ${STATE_GROUP} missing"
    if [ -f "${WS_ENV}" ]; then
        echo "config:      ✓ ${WS_ENV}"
    else
        echo "config:      ✗ ${WS_ENV} missing"
    fi
    if [ -f "${SERVICE_DEST}" ]; then
        for profile in "${PROFILES[@]}"; do
            local sock="/run/euler/ws-${profile}.sock"
            local health="unreachable"
            if sudo test -S "${sock}" && \
               sudo curl -sf --max-time 3 --unix-socket "${sock}" http://x/healthz > /dev/null 2>&1; then
                health="serving"
            fi
            echo "euler-ws@${profile}: $(systemctl is-active "euler-ws@${profile}.service" 2>/dev/null)/$(systemctl is-enabled "euler-ws@${profile}.service" 2>/dev/null) · ${sock} ${health}"
        done
    else
        echo "units:       deferred (solver.web.ws not yet deployed)"
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

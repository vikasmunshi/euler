#!/usr/bin/env bash
# Content service kit (euler-content) — Phase 5a-2 of the server redesign (DD-5/DD-12)
# ====================================================================================
#
# Installs / uninstalls / upgrades the OS layer for the content service: the
# **per-profile** service identities and the content-tree ACLs that back the app's
# authorization at the filesystem, plus the systemd **template unit**
# `euler-content@<profile>.service` (one instance per web profile), all running
# from the shared root-owned /opt/euler system venv (DD-5). Sibling to
# frontend.sh / auth.sh / egress.sh / firewall.sh; see docs/secure-web-server.md
# (Phase 5, DD-12).
#
# The per-profile model (DD-12):
#   - All web users share one uid within a single service process, so the filesystem
#     cannot tell a `reader` request from a `contributor` one. To make the OS layer
#     real per-profile, the content service runs as **per-profile instances** —
#     `euler-content@<profile>.service`, each `User=euler-content-<profile>` on its
#     own socket `/run/euler/content-<profile>.sock` — and Caddy routes by the
#     `X-Profile` that forward_auth returns to the matching instance (frontend.sh).
#     No process changes uid (no root, no setuid): each instance is *born* right.
#     The app also pins `EULER_PROFILE=<profile>` and refuses a mismatched
#     `X-Profile` (the code-side backstop; solver/web/site).
#   - `admin` is local-only and web profiles cap at `maintainer` (DD-11), so only
#     three web instances exist: reader, contributor, maintainer.
#
# The content-tree ACLs (refines DD-5):
#   - The services read/write the repo **working tree directly** — the git filter
#     leaves plaintext at rest, so the tier needs *filesystem access, not the key*,
#     and does no git operations. Access is a scoped ACL derived from
#     authorizations.json's `objects`→paths (the single source, so app policy and
#     filesystem enforcement can't drift):
#       euler-sol-read    rX  on docs/ · topics/ · solutions/ · solver/web/content/  (reader+)
#       euler-sol-write   rwX on solutions/                                (contributor+)
#       euler-sol-delete  rwX on solutions/  (POSIX: delete = dir-write)   (maintainer)
#     plus a traverse-only ACL (g:euler-web:x) on the home path + repo root so the
#     uids can *reach* those subtrees without reading the rest of home.
#   - `.git`, `keys/` (enc-key.json), and the `solver/` source are **never** in the
#     ACL set — the script refuses any target under them. The master key never
#     reaches the services (AR-2).
#
#   /opt/euler/venv                            root:euler-web 0755  (shared venv, DD-5)
#   /etc/euler/content.env                     root:euler-web 0640  (generated here)
#   /etc/systemd/system/euler-content@.service (root-owned template; instances enabled
#                                               per web profile; deferred until
#                                               solver.web.site exists in the venv)
#
# Because the units live in root's systemd and run as locked-down users, lifecycle
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
HOME_DIR="$(dirname "${PROJECT_ROOT}")"                 # the operator home the repo lives in

SYS_DIR="/etc/euler"
CONTENT_ENV="${SYS_DIR}/content.env"                    # scoped runtime config (root:euler-web 0640)
AUTHZ_FILE="${SYS_DIR}/authorizations.json"             # DD-12 SoR (deployed by auth.sh)
AUTHZ_TEMPLATE="${PROJECT_ROOT}/solver/templates/authorizations.json"  # fallback before auth.sh runs
OPT_DIR="/opt/euler"
VENV_DIR="${OPT_DIR}/venv"
VENV_PY="${VENV_DIR}/bin/python"

PYTHON="python3.14"                                     # the project floor; deadsnakes on 24.04

WEB_GROUP="euler-web"
# The web profiles that get an instance (admin is local-only; web caps at maintainer, DD-11).
PROFILES=(reader contributor maintainer)
# Content-tree ACL groups (mapped to the per-profile uids below).
SOL_READ_GROUP="euler-sol-read"
SOL_WRITE_GROUP="euler-sol-write"
SOL_DELETE_GROUP="euler-sol-delete"

SERVICE_TEMPLATE="euler-content@.service"
SERVICE_DEST="/etc/systemd/system/${SERVICE_TEMPLATE}"

# Content subtrees, resolved from authorizations.json (set by resolve_content_paths).
READ_PATHS=()
WRITE_PATHS=()
DELETE_PATHS=()

usage() {
    cat <<USAGE
Usage: $0 [install|uninstall|upgrade|redeploy|status|help]

  install    Create the per-profile euler-content-<profile> identities and the
             euler-sol-{read,write,delete} ACL groups, apply the content-tree ACLs
             (derived from authorizations.json), deploy /etc/euler/content.env, and
             — when solver.web.site exists in the /opt/euler venv — install the
             root-owned euler-content@.service template and enable an instance per
             web profile (reader, contributor, maintainer).
  uninstall  Disable the instances, remove the unit + content.env, strip the
             content-tree ACLs, and (prompted) remove the identities/groups.
  upgrade    Re-assert identities, ACLs, config, and units; restart the instances.
  redeploy   Fast path: refresh /etc/euler/content.env and restart the per-profile
             instances to pick up new code — no identities, ACLs, or unit changes.
             (The shared /opt/euler venv is rebuilt by 'auth.sh redeploy'.)
  status     Show venv/deps, identities, ACL groups, config, and instance health.

  Requires: the /opt/euler venv (auth.sh) and the acl package (auto-installed).
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
        echo "Error: systemd is required for the content service; it is not active here." >&2
        return 1
    fi
}

require_python() {
    if ! command -v "${PYTHON}" &> /dev/null; then
        echo "Error: ${PYTHON} not found — run 'make install-system' (deadsnakes) first." >&2
        return 1
    fi
}

# The acl package (setfacl/getfacl) backs the content-tree grants — install if absent.
require_acl() {
    if command -v setfacl &> /dev/null; then
        return 0
    fi
    echo "Installing the acl package (setfacl) for the content-tree ACLs..."
    sudo apt-get install -y acl
}

# Resolve the content subtrees from authorizations.json's objects map (the deployed SoR
# if present, else the repo template) so the ACLs can never drift from the app policy.
# READ  = docs (incl. topics/) + solutions + web-content + about (the footer files);
# WRITE/DELETE = solutions. Absolute or empty object paths (e.g. shell:/bin/bash)
# are ignored — only repo-relative content trees/files.
resolve_content_paths() {
    local src="${AUTHZ_TEMPLATE}"
    [ -f "${AUTHZ_FILE}" ] && src="${AUTHZ_FILE}"
    local out
    out="$("${PYTHON}" - "${src}" <<'PY'
import json, sys
objs = json.loads(open(sys.argv[1]).read()).get('objects', {})
def paths(name):
    return [p for p in objs.get(name, []) if p and not p.startswith('/')]
read = paths('docs') + paths('solutions') + paths('web-content') + paths('about')
print('READ\t' + '\t'.join(dict.fromkeys(read)))     # de-dup, keep order
print('WRITE\t' + '\t'.join(paths('solutions')))
print('DELETE\t' + '\t'.join(paths('solutions')))
PY
)"
    READ_PATHS=();  WRITE_PATHS=();  DELETE_PATHS=()
    local line kind rest
    while IFS=$'\t' read -r kind rest; do
        # shellcheck disable=SC2206
        local arr=(${rest})
        case "${kind}" in
            READ)   READ_PATHS=("${arr[@]}") ;;
            WRITE)  WRITE_PATHS=("${arr[@]}") ;;
            DELETE) DELETE_PATHS=("${arr[@]}") ;;
        esac
    done <<< "${out}"
    # Safety: no content path may resolve under .git/, keys/, or the solver/ source
    # — except the two deliberately viewable subtrees, solver/web/content/ and
    # solver/templates/ (the doc-referenced code/prompt templates + the non-secret
    # authorizations template). The master key, history, and app source stay out.
    local rel abs
    for rel in "${READ_PATHS[@]}" "${WRITE_PATHS[@]}" "${DELETE_PATHS[@]}"; do
        abs="${PROJECT_ROOT}/${rel}"
        case "${rel%/}" in
            .git | .git/* | keys | keys/* | solver | solver/ai* | solver/auth* | solver/core* | solver/crypto* | solver/runners* | solver/shell* | solver/utils* | solver/web/auth*)
                echo "Error: refusing to ACL a protected path: ${rel}" >&2; return 1 ;;
        esac
        if [ ! -e "${abs}" ]; then
            echo "Warning: content path ${abs} does not exist — skipping" >&2
        fi
    done
}

# Create the per-profile identities and ACL groups (idempotent).
#   euler-sol-read/write/delete  — the content-tree ACL groups.
#   euler-content-<profile>      — own primary group + euler-web + the sol groups its
#                                  profile is entitled to (systemd loads the uid's full
#                                  group list, so no SupplementaryGroups= in the unit).
ensure_identities() {
    local grp
    for grp in "${WEB_GROUP}" "${SOL_READ_GROUP}" "${SOL_WRITE_GROUP}" "${SOL_DELETE_GROUP}"; do
        getent group "${grp}" > /dev/null || sudo groupadd --system "${grp}"
    done

    local profile user own_group extra
    for profile in "${PROFILES[@]}"; do
        user="euler-content-${profile}"
        own_group="${user}"
        case "${profile}" in
            reader)      extra="${WEB_GROUP},${SOL_READ_GROUP}" ;;
            contributor) extra="${WEB_GROUP},${SOL_READ_GROUP},${SOL_WRITE_GROUP}" ;;
            maintainer)  extra="${WEB_GROUP},${SOL_READ_GROUP},${SOL_WRITE_GROUP},${SOL_DELETE_GROUP}" ;;
            *)           extra="${WEB_GROUP},${SOL_READ_GROUP}" ;;
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
# package always matches the current source — the units run `-m solver.web.site` from
# it (cwd=/, so a stale venv fails even when the repo has the module). auth.sh builds
# the same venv; installing again here is idempotent and keeps content.sh self-sufficient.
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
    # nh3 rides along: the DD-10 kit check that the .html save gate (5c) can import.
    if sudo "${VENV_PY}" -P -c 'import solver.web.site, nh3' 2>/dev/null; then
        echo "Deployed: ✓ solver.web.site (+ nh3) importable from ${VENV_DIR}"
    else
        echo "Deployed: ✗ solver.web.site (or nh3) NOT importable from the venv" >&2
    fi
}

# The repo's GitHub URL, for the problem pages' source links. Resolved here, at
# deploy time, because the service uid cannot read .git (DD-12) — and normalised to
# the browsable https form (git@github.com:o/r.git → https://github.com/o/r). Empty
# output leaves the app's built-in default in place.
github_url() {
    git -C "${PROJECT_ROOT}" remote get-url origin 2>/dev/null |
        sed -e 's#^git@\([^:]*\):#https://\1/#' -e 's#\.git$##'
}

# Scoped runtime config for the content instances (never the full ~/.euler/env): the
# per-instance EULER_PROFILE / EULER_CONTENT_SOCKET come from the template unit (%i).
deploy_content_env() {
    sudo mkdir -p "${SYS_DIR}"
    local repo_url
    repo_url="$(github_url)"
    sudo tee "${CONTENT_ENV}" > /dev/null <<EOF
# GENERATED by scripts/setup/content.sh — scoped runtime config for euler-content (DD-12).
# The per-instance EULER_PROFILE and EULER_CONTENT_SOCKET are set by the template unit.
EULER_REPO_ROOT=${PROJECT_ROOT}
EULER_WEB_GROUP=${WEB_GROUP}
${repo_url:+EULER_GITHUB_URL=${repo_url}}
EOF
    sudo chown root:"${WEB_GROUP}" "${CONTENT_ENV}"
    sudo chmod 0640 "${CONTENT_ENV}"
}

# Apply the content-tree ACLs (DD-12). Traverse-only on the home path + repo root so
# the uids can descend to the content subtrees without reading the rest of home; then
# per-subtree read/write ACLs (recursive + default, so new files inherit). Idempotent.
deploy_acls() {
    require_acl
    echo "Applying content-tree ACLs (traverse: ${HOME_DIR}, ${PROJECT_ROOT})..."
    sudo setfacl -m "g:${WEB_GROUP}:x" "${HOME_DIR}" "${PROJECT_ROOT}"

    local rel abs
    for rel in "${READ_PATHS[@]}"; do
        abs="${PROJECT_ROOT}/${rel%/}"
        [ -e "${abs}" ] || continue
        echo "  read  (${SOL_READ_GROUP}:rX)  ${rel}"
        sudo setfacl -R  -m "g:${SOL_READ_GROUP}:rX" "${abs}"
        # Default (inherit) ACLs exist only on directories — the `about` object
        # maps single files (README.md, LICENSE, …), which take just the plain ACL.
        if [ -d "${abs}" ]; then
            sudo setfacl -R -d -m "g:${SOL_READ_GROUP}:rX" "${abs}"
        fi
    done
    for rel in "${WRITE_PATHS[@]}"; do
        abs="${PROJECT_ROOT}/${rel%/}"
        [ -e "${abs}" ] || continue
        echo "  write (${SOL_WRITE_GROUP}:rwX) ${rel}"
        sudo setfacl -R  -m "g:${SOL_WRITE_GROUP}:rwX" "${abs}"
        sudo setfacl -R -d -m "g:${SOL_WRITE_GROUP}:rwX" "${abs}"
    done
    # POSIX ACLs cannot separate unlink from write (delete = write on the containing
    # dir), so the delete group carries the same rwX; the write/delete *split* is
    # enforced at the app layer (requires solutions:delete). The group is kept distinct
    # so maintainer-only membership still mirrors the app grant set.
    for rel in "${DELETE_PATHS[@]}"; do
        abs="${PROJECT_ROOT}/${rel%/}"
        [ -e "${abs}" ] || continue
        echo "  delete(${SOL_DELETE_GROUP}:rwX) ${rel}"
        sudo setfacl -R  -m "g:${SOL_DELETE_GROUP}:rwX" "${abs}"
        sudo setfacl -R -d -m "g:${SOL_DELETE_GROUP}:rwX" "${abs}"
    done
}

# Remove the content-tree ACLs added by deploy_acls (best-effort; leaves owner perms).
strip_acls() {
    command -v setfacl &> /dev/null || return 0
    echo "Stripping content-tree ACLs..."
    sudo setfacl -x "g:${WEB_GROUP}" "${HOME_DIR}" "${PROJECT_ROOT}" 2>/dev/null || true
    local rel abs grp
    for rel in "${READ_PATHS[@]}" "${WRITE_PATHS[@]}" "${DELETE_PATHS[@]}"; do
        abs="${PROJECT_ROOT}/${rel%/}"
        [ -e "${abs}" ] || continue
        for grp in "${SOL_READ_GROUP}" "${SOL_WRITE_GROUP}" "${SOL_DELETE_GROUP}"; do
            sudo setfacl -R  -x "g:${grp}" "${abs}" 2>/dev/null || true
            sudo setfacl -R -d -x "g:${grp}" "${abs}" 2>/dev/null || true
        done
    done
}

# True when the deployed venv contains the content-service module (build-order gate).
# -P ignores cwd, so this tests the venv's site-packages, not the repo we run from.
venv_has_site() {
    [ -x "${VENV_PY}" ] && sudo "${VENV_PY}" -P -c 'import solver.web.site' 2>/dev/null
}

# Install the root-owned template unit and enable one instance per web profile.
install_units() {
    echo "Installing ${SERVICE_TEMPLATE} (per-profile, loopback-only)..."
    sudo tee "${SERVICE_DEST}" > /dev/null <<EOF
[Unit]
Description=euler content service (%i) — server-rendered pages + htmx (Phase 5, DD-12)
Documentation=https://github.com/vikasmunshi/euler/blob/master/docs/secure-web-server.md
After=network.target euler-auth.service
Wants=euler-auth.service

[Service]
Type=simple
# Born as the per-profile uid — no setuid, no root. systemd loads the uid's full
# group list (euler-web + the euler-sol-* it is entitled to) from the user database.
User=euler-content-%i
EnvironmentFile=${CONTENT_ENV}
Environment=EULER_PROFILE=%i
Environment=EULER_CONTENT_SOCKET=/run/euler/content-%i.sock
ExecStart=${VENV_PY} -m solver.web.site
Restart=on-failure
RestartSec=5s

# DD-8 layer 1: the content service is loopback-only (Caddy over the unix socket).
IPAddressDeny=any
IPAddressAllow=localhost

# Hardening. Unlike euler-auth, the content service reads the repo working tree under
# the operator home, so ProtectHome must stay off — the content-tree ACLs (not the
# sandbox) confine which subtrees the uid can reach. ProtectSystem=strict keeps the
# whole FS read-only except the socket dir and the writable solutions subtree; the
# per-profile ACL still denies writes to the reader uid.
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=false
ReadWritePaths=/run/euler ${PROJECT_ROOT}/solutions
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
    restart_instances
}

# Restart every per-profile instance (they re-exec the /opt/euler venv, picking up
# freshly deployed code). Enable --now so a not-yet-started instance comes up too.
restart_instances() {
    local profile
    for profile in "${PROFILES[@]}"; do
        sudo systemctl enable --now "euler-content@${profile}.service"
        sudo systemctl restart "euler-content@${profile}.service"
    done
}

# ── install / uninstall ───────────────────────────────────────────────────────────

do_install() {
    check_can_sudo || return 1
    require_systemd || return 1
    require_python || return 1
    resolve_content_paths || return 1
    ensure_identities
    deploy_venv
    deploy_content_env
    deploy_acls

    if venv_has_site; then
        install_units
    else
        echo "note: solver.web.site not yet in the deployed package — instances deferred"
        echo "      (re-run '$0 upgrade' once the venv carries it)."
    fi

    # The per-profile uids are part of the nftables egress ruleset — regenerate.
    if [ -f /etc/systemd/system/euler-firewall.service ]; then
        echo "Reloading the egress firewall to include the euler-content-* uids..."
        "${SCRIPT_DIR}/firewall.sh" reload
    fi
    do_status
}

# Fast redeploy: refresh content.env and restart the instances so they re-exec the
# freshly rebuilt /opt/euler venv (rebuilt by 'auth.sh redeploy'). No identities,
# ACLs, unit re-lay, or firewall reload.
do_redeploy() {
    check_can_sudo || return 1
    require_systemd || return 1
    deploy_content_env
    if [ -f "${SERVICE_DEST}" ] && venv_has_site; then
        restart_instances
        echo "Restarted the per-profile content instances."
    else
        echo "note: content instances not installed yet — run '$0 install'."
    fi
    do_status
}

do_uninstall() {
    check_can_sudo || return 1
    resolve_content_paths || true
    if [ -f "${SERVICE_DEST}" ]; then
        local profile
        for profile in "${PROFILES[@]}"; do
            sudo systemctl disable --now "euler-content@${profile}.service" 2>/dev/null || true
        done
        sudo rm -f "${SERVICE_DEST}"
        sudo systemctl daemon-reload
    fi
    sudo rm -f "${CONTENT_ENV}"

    local reply
    read -r -p "Strip the content-tree ACLs from ${PROJECT_ROOT}? [y/N] " reply
    [[ "${reply}" =~ ^[Yy]$ ]] && strip_acls

    read -r -p "Remove the euler-content-* identities and euler-sol-* groups? [y/N] " reply
    if [[ "${reply}" =~ ^[Yy]$ ]]; then
        local profile user
        for profile in "${PROFILES[@]}"; do
            user="euler-content-${profile}"
            getent passwd "${user}" > /dev/null && sudo userdel "${user}" 2>/dev/null || true
            getent group  "${user}" > /dev/null && sudo groupdel "${user}" 2>/dev/null || true
        done
        local grp
        for grp in "${SOL_READ_GROUP}" "${SOL_WRITE_GROUP}" "${SOL_DELETE_GROUP}"; do
            getent group "${grp}" > /dev/null && sudo groupdel "${grp}" 2>/dev/null || true
        done
    fi
    echo "Content service uninstall complete."
}

# ── status ────────────────────────────────────────────────────────────────────────

do_status() {
    if [ -x "${VENV_PY}" ]; then
        if "${VENV_PY}" -P -c 'import solver.web.site, nh3' 2>/dev/null; then
            echo "venv:        ✓ solver.web.site (+ nh3) importable from ${VENV_DIR}"
        else
            echo "venv:        ✗ solver.web.site (or nh3) not importable from the venv"
        fi
    else
        echo "venv:        ✗ ${VENV_DIR} not deployed (run auth.sh / content.sh install)"
    fi
    local profile user
    for profile in "${PROFILES[@]}"; do
        user="euler-content-${profile}"
        if getent passwd "${user}" > /dev/null; then
            echo "identity:    ✓ ${user} (groups: $(id -nG "${user}" 2>/dev/null))"
        else
            echo "identity:    ✗ ${user} missing"
        fi
    done
    local grp
    for grp in "${SOL_READ_GROUP}" "${SOL_WRITE_GROUP}" "${SOL_DELETE_GROUP}"; do
        getent group "${grp}" > /dev/null && echo "acl group:   ✓ ${grp}" || echo "acl group:   ✗ ${grp} missing"
    done
    if [ -f "${CONTENT_ENV}" ]; then
        echo "config:      ✓ ${CONTENT_ENV}"
    else
        echo "config:      ✗ ${CONTENT_ENV} missing"
    fi
    if [ -f "${SERVICE_DEST}" ]; then
        for profile in "${PROFILES[@]}"; do
            echo "euler-content@${profile}: $(systemctl is-active "euler-content@${profile}.service" 2>/dev/null)/$(systemctl is-enabled "euler-content@${profile}.service" 2>/dev/null)"
        done
    else
        echo "units:       deferred (solver.web.site not yet deployed)"
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

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
#     provision   create the uid <slug> + home /home/<slug> (0700), clone ~/euler DIRECTLY from
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
# Actions: deploy | remove | upgrade | redeploy | provision | deprovision | purge-legacy |
#          status | help
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
# Parent group: every per-user uid joins it. It is also the ROSTER — the per-user uids are
# named for the slug alone (ue0f4a1), so there is no name prefix left to enumerate them by,
# and this root-owned membership is what identifies them here, in firewall.sh, and in
# solver.auth.identity (per_user_login).
USER_GROUP="euler-user"
USER_HOME_BASE="/home"                                 # per-user homes: /home/<slug>

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
                               user's git hooks (and the .gitignore / .shellcheckrc they
                               read) from this repo, and stop the running instances so
                               their sockets re-activate them against a freshly rebuilt
                               venv (drops live shells).
  provision <slug> <email> <profile>
                               Provision one collaborator: the uid <slug> + /home/<slug> (0700), a
                               filter-disabled clone of ~/euler from the public GitHub
                               repo on branch user/<slug> (cloned AS the user, through
                               Squid), git hooks rendered from THIS repo's templates
                               plus the .gitignore / .shellcheckrc they read,
                               Claude Code (~/.local/bin, theirs), ~/.euler, and the
                               instance socket. Idempotent — re-run it to repair an
                               instance and re-lay its hooks; the clone is left as it
                               stands (this plane cannot sync it).
  deprovision <slug>           Tear one collaborator down: stop/disable the instance,
                               then (prompted) userdel + remove the home. Reports the
                               required 'key-rekey' to drop master-key access.
  purge-legacy                 One-shot migration sweep: remove any euler-user account
                               left from the retired euler-user-<slug> naming scheme
                               (prompted — accounts, homes and units all go).
  status [<slug>]              Show the shared layer, or one user's instance health,
                               including whether their web shell is live and connected.

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

# A slug is exactly what solver.auth.identity.system_slug emits: 'u' + a hex digest of the
# e-mail. Matching that shape exactly matters more now than it did behind the retired
# euler-user- prefix: the slug IS the uid, so it is a bare name in the shared account
# namespace, and a loose pattern would let a typo'd call provision (or, worse, adopt) an
# ordinary login name. It also becomes a home path, a socket name, and a git branch.
valid_slug() {
    [[ "$1" =~ ^u[0-9a-f]{6,16}$ ]]
}

require_slug() {
    if ! valid_slug "${1:-}"; then
        echo "Error: '${1:-}' is not a valid system slug (expected ^u[0-9a-f]{6,16}\$)." >&2
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
SocketUser=%i
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
# Born as the collaborator's own uid — no setuid, no root. The uid IS the slug (%i); it
# owns its home, its clone, and its vault, and the kernel (SO_PEERCRED) is the
# authoritative identity.
User=%i
EnvironmentFile=${USER_ENV}
# HTTPS_PROXY: the problem scraper egresses only through Squid.
EnvironmentFile=-${EGRESS_ENV}
Environment=EULER_USER_SLUG=%i
Environment=EULER_REPO_ROOT=${USER_HOME_BASE}/%i/euler
ExecStart=${VENV_PY} -m solver.web.user
Restart=on-failure
RestartSec=5s

# Egress layer 1: loopback only — the /run/euler sockets and the Squid proxy. The kernel
# firewall (firewall.sh, scoped to the euler-user group's uids) is layer 2.
IPAddressDeny=any
IPAddressAllow=localhost

# Hardening. This tier runs the user's own code by design, contained to
# THIS user's uid — their home, their keys, their clone, no one else's. The sandbox
# must not break the code being run (native extensions need W^X), so containment is the
# uid + egress lock, not a syscall jail.
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=false
ReadWritePaths=/run/euler ${USER_HOME_BASE}/%i
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

# The uid IS the slug (ue0f4a1) — no prefix, so the home is /home/<slug> and the unit
# instance name, the socket, the uid and the home all read the same.
user_of()  { echo "$1"; }
home_of()  { echo "${USER_HOME_BASE}/$1"; }
sock_of()  { echo "/run/euler/user-$1.sock"; }

# The per-user roster, by group membership. With the euler-user- name prefix gone there is
# nothing to grep /etc/passwd for; the parent group is the enumerable set (and the same one
# solver.auth.identity.per_user_login and firewall.sh read). Lists the group's members,
# one per line, most-recent-last; empty when none are provisioned.
euler_user_names() {
    getent group "${USER_GROUP}" 2>/dev/null | awk -F: '{print $4}' | tr ',' '\n' | sed '/^$/d'
}

# True if <name> is one of ours. Provisioning must never ADOPT an account it did not
# create: the slug is now a bare name in the shared login namespace, so a pre-existing
# 'ue0f4a1' would otherwise be handed a service unit, a home rewrite, and a clone.
is_euler_user() {
    euler_user_names | grep -qx "$1"
}

ensure_user_identity() {
    local slug="$1" user home
    user="$(user_of "${slug}")"
    home="$(home_of "${slug}")"
    if getent passwd "${user}" > /dev/null && ! is_euler_user "${user}"; then
        echo "Error: an account named '${user}' already exists and is not in ${USER_GROUP}." >&2
        echo "       Refusing to adopt it — a per-user instance must own its uid outright." >&2
        return 1
    fi
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
# The per-user uids are inside the egress lock (firewall.sh), so the script first
# sources /etc/euler/egress.env: outbound HTTP(S) goes through Squid or not at all
# (root, by contrast, bypassed the lock — one more reason not to work as root).
as_user() {
    local user="$1"; shift
    sudo -Hu "${user}" env "$@" EGRESS_ENV="${EGRESS_ENV}" bash -s
}

# Lay the git hooks — and the repo-root config they read — into a provisioned clone,
# rendered from THIS repo's templates.
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
# whose source sits in the operator's 0750 home: the per-user uids cannot read it, so
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
    provision_hook_config "${slug}"
    provision_filter_command "${slug}"
}

# Restore the two repo-root files the hooks READ, from this checkout into the clone.
#
# A hook is only as good as its configuration, and both of these are configuration:
# `.gitignore` decides the pre-commit "gitignored files" verdict (its `!` negations are what
# keep a tracked dotfile from reading as ignored), and `.shellcheckrc` decides how every
# shell script is judged — `external-sources` above all, without which a script passes or
# fails on whether the file it sources happened to be in the same shellcheck command. Ship
# the hook from here and leave its config to the clone, and the gate a collaborator runs is
# not the gate this repo chose.
#
# Copied ONLY when the clone's own HEAD already holds these exact bytes. That looks like a
# no-op and is precisely the point: it puts the file back when a collaborator has edited
# theirs, which is the only case where the two can disagree without git being involved.
#
# It is deliberately SKIPPED when the clone is behind on the file, and this is not caution —
# it is the difference between a missing config and an unusable clone. Git refuses to merge
# over a path whose worktree copy differs from HEAD: untracked, or tracked-and-modified, and
# even when the bytes are byte-identical to what the merge is bringing in (both cases
# verified). Copying into a behind clone would therefore trade "your shellcheck lane is
# unconfigured until you sync" for "you cannot sync at all" — and the sync is exactly what
# fixes the first. So the file waits for `git-sync`, which is the plane that can deliver it,
# and the operator is told which clones are waiting.
provision_hook_config() {
    local slug="$1" user clone name src ours theirs
    user="$(user_of "${slug}")"
    clone="$(home_of "${slug}")/euler"
    for name in .gitignore .shellcheckrc; do
        src="${PROJECT_ROOT}/${name}"
        if [ ! -f "${src}" ]; then
            echo "warn: ${src} not found — skipping ${name}." >&2
            continue
        fi
        # Blob hashes, not file contents: `rev-parse HEAD:<path>` is what the clone has
        # COMMITTED, so this compares against the clone's own history and not its worktree —
        # a worktree the collaborator may have edited, which is the case being repaired.
        ours="$(git -C "${PROJECT_ROOT}" hash-object -- "${src}" 2> /dev/null || true)"
        theirs="$(sudo -u "${user}" git -C "${clone}" rev-parse "HEAD:${name}" 2> /dev/null || true)"
        if [ -z "${ours}" ] || [ "${ours}" != "${theirs}" ]; then
            echo "note: ${clone} is behind on ${name} — it arrives when ${slug} runs git-sync."
            continue
        fi
        sudo install -o "${user}" -g "${user}" -m 0644 "${src}" "${clone}/${name}"
        echo "Installed config: ${name}"
    done
}

# Point a clone's crypt filter at the deployed venv, with -P.
#
# A clone keeps whatever filter command was recorded the day it was wired, and only
# `git-filter install` rewrites it — which needs the master key, so it can run in the
# collaborator's own session and nowhere else. That makes a change to this command the one
# piece of per-clone setup they cannot receive: it waits for them to happen to save a key.
#
# -P is why that matters. git runs a filter with the cwd at the top of the worktree, and a
# solver checkout has a `solver/` package sitting right there — without -P the filter imports
# THE CLONE's source instead of the venv's, so a clone that falls behind runs an old filter
# against a current key file and stops decrypting. Writing the command here needs no key
# (only the re-checkout does, and their tree is already plaintext), so the operator can push
# it to every clone at once, the same way the hooks go out.
provision_filter_command() {
    local slug="$1" user clone base
    user="$(user_of "${slug}")"
    clone="$(home_of "${slug}")/euler"
    base="${VENV_DIR}/bin/python -P -m solver.crypto.gitfilter"
    if ! sudo -u "${user}" git -C "${clone}" config --local --get filter.solver-crypt.process \
        > /dev/null 2>&1; then
        return 0                    # unwired: theirs to wire when they are issued a key
    fi
    for action in process clean smudge; do
        sudo -u "${user}" git -C "${clone}" config --local \
            "filter.solver-crypt.${action}" "${base} ${action}"
    done
    echo "Filter command points at ${VENV_DIR} (-P)"
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
    # the internet directly, bypassing Squid. firewall.sh enumerates the per-user uids by group.
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

# Sweep out accounts from the RETIRED naming scheme — the `euler-user-<slug>` uids
# provisioned before the uid became the slug itself. They are still euler-user group
# members, so they still hold an egress-locked uid and a home full of a collaborator's
# clone, but nothing else lines up any more: `deprovision` rejects their name (it is not
# a valid slug), their unit instance is named for the suffix, and Caddy would dial a
# socket named for the NEW slug of the same e-mail. Rather than teach every path two
# naming schemes for a handful of accounts, this removes them wholesale; the affected
# collaborators are re-invited and re-onboarded under their new uid.
do_purge_legacy() {
    check_can_sudo || return 1
    local legacy=() name reply instance
    while read -r name; do
        [ -n "${name}" ] && ! valid_slug "${name}" && legacy+=("${name}")
    done < <(euler_user_names || true)
    if [ ${#legacy[@]} -eq 0 ]; then
        echo "No legacy per-user accounts found — every ${USER_GROUP} member is a valid slug."
        return 0
    fi
    echo "Legacy per-user accounts (retired naming scheme):"
    printf '  %s\n' "${legacy[@]}"
    echo
    echo "IMPORTANT: removing an account does NOT revoke its master-key access. For any of"
    echo "           these whose key was user-authorized, run \`key-rekey\` in the shell"
    echo "           afterwards to rotate the master key onto the remaining users."
    echo
    read -r -p "Remove these accounts and their homes? [y/N] " reply
    [[ "${reply}" =~ ^[Yy]$ ]] || { echo "Left in place."; return 0; }
    for name in "${legacy[@]}"; do
        instance="${name#euler-user-}"                   # how the old unit was instantiated
        sudo systemctl disable --now "euler-user@${instance}.socket"  2>/dev/null || true
        sudo systemctl disable --now "euler-user@${instance}.service" 2>/dev/null || true
        sudo rm -f "$(sock_of "${instance}")"
        sudo userdel --remove "${name}" 2>/dev/null || sudo userdel "${name}" 2>/dev/null || true
        getent group "${name}" > /dev/null && sudo groupdel "${name}" 2>/dev/null || true
        sudo rm -rf "${USER_HOME_BASE:?}/${name}"
        echo "Removed ${name} and ${USER_HOME_BASE}/${name}."
    done
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
    local users slug
    users="$(euler_user_names || true)"
    for slug in ${users}; do
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
    leftover="$(euler_user_names || true)"
    if [ -n "${leftover}" ]; then
        echo "Refusing to uninstall — provisioned users remain:" >&2
        # shellcheck disable=SC2001  # per-line indent of a multi-line string; ${//} can't anchor ^
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

    # Per-user roster (or one slug's instance), each reported by unix name + e-mail alias.
    load_aliases
    local slug="${1:-}"
    if [ -n "${slug}" ]; then
        status_line "users" "${OK}" "1 requested"
        status_one "${slug}"
        return 0
    fi
    local users slug_
    users="$(euler_user_names || true)"
    if [ -z "${users}" ]; then
        status_line "users" "${DEFER}" "none provisioned"
        return 0
    fi
    status_line "users" "${OK}" "$(wc -l <<< "${users}") provisioned"
    for slug_ in ${users}; do
        status_one "${slug_}"
    done
}

# ── the per-user report ───────────────────────────────────────────────────────────────
#
# A collaborator is reported BY UNIX NAME (the slug — that is what the uid, the home, the
# socket, the unit instance and the branch are all called) with their **e-mail as an
# alias**. The alias has to be looked up rather than read off the name: the slug is a hash
# of the e-mail, so the only way back is to recompute system_slug() for every identity in
# the deployed policy and index by the result. A slug with no alias is an account the
# policy no longer maps (deprovision it, or re-add the user).

AUTHZ_FILE="${SYS_DIR}/authorizations.json"

# system_slug(email) for each mapped web identity → "<slug> <email> <profile>".
_ALIAS_PY='
import json, sys
from solver.auth.identity import system_slug
try:
    users = json.load(open(sys.argv[1])).get("users", {})
except (OSError, ValueError):
    raise SystemExit(0)
for email, profile in sorted(users.items()):
    if "@" in email:
        print(system_slug(email), email, profile)
'

declare -A USER_ALIAS=()

# Populate USER_ALIAS[slug] = "<email> <profile>". Needs the deployed venv (it imports
# solver.auth.identity, the one definition of the mapping); silently leaves the map empty
# when the venv or the policy file is absent — the report then shows slugs alone.
load_aliases() {
    [ -x "${VENV_PY}" ] || return 0
    local slug email profile
    while read -r slug email profile; do
        [ -n "${slug}" ] && USER_ALIAS["${slug}"]="${email} (${profile})"
    done < <(sudo "${VENV_PY}" -P -c "${_ALIAS_PY}" "${AUTHZ_FILE}" 2>/dev/null || true)
}

# Ask a RUNNING instance what its web shell is doing: GET /internal/status over that
# user's own socket. Root can connect whatever the 0660 mode says.
#
# Only ever called when the service is already active. Dialing the socket is what
# *starts* an instance (it is socket-activated), so an unconditional probe would fork a
# service — and a whole PTY-less python process — for every idle collaborator, which is a
# strange thing for a status command to do.
#
# The reply is reduced by _SHELL_PY to one line — "none", "unreadable", or
# "live <attached> <detached-seconds> <pid>" — and this function turns that into the
# marked phrase; there is at most one shell per instance (one user, one PtyManager key).
_SHELL_PY='
import json, sys
try:
    shells = json.loads(sys.argv[1]).get("shells") or []
except ValueError:
    print("unreadable"); raise SystemExit(0)
live = [s for s in shells if s.get("alive")]
if not live:
    print("none"); raise SystemExit(0)
s = live[0]
print("live", int(s.get("attached", 0)), int(float(s.get("detached_for", 0))), s.get("pid", "?"))
'

shell_state() {
    local slug="$1" payload state attached detached pid
    if ! command -v curl > /dev/null 2>&1; then
        printf '%s unknown (curl not installed)' "${DEFER}"
        return 0
    fi
    payload="$(sudo curl -sS --max-time 3 --unix-socket "$(sock_of "${slug}")" \
                    http://localhost/internal/status 2>/dev/null || true)"
    if [ -z "${payload}" ]; then
        printf '%s unreachable (instance running, /internal/status silent)' "${BAD}"
        return 0
    fi
    # `|| true`: a silent reducer leaves read at EOF, and a bare failing read would take
    # `set -e` down with it — a status probe must never abort the sweep.
    read -r state attached detached pid \
        < <("${PYTHON}" -c "${_SHELL_PY}" "${payload}" 2>/dev/null || true) || true
    case "${state:-}" in                    # ':-' — a failed read leaves it unset (set -u)
        live)
            if [ "${attached:-0}" -gt 0 ]; then
                printf '%s live · connected (%s terminal(s)) · pid %s' "${OK}" "${attached}" "${pid}"
            else
                printf '%s live · NOT connected (detached %ss) · pid %s' "${OK}" "${detached}" "${pid}"
            fi ;;
        none) printf '%s none (instance running, no shell forked)' "${DEFER}" ;;
        *)    printf '%s unreadable reply from /internal/status' "${BAD}" ;;
    esac
}

# Two lines per collaborator: the identity line (unix name + e-mail alias), then the
# instance line and the shell line, every field marked.
status_one() {
    local slug="$1" user home clone socket service shell
    user="$(user_of "${slug}")"
    home="$(home_of "${slug}")"
    clone="${home}/euler"
    printf '  %-10s %s\n' "${slug}" "${USER_ALIAS[${slug}]:-<no mapped e-mail>}"
    if ! getent passwd "${user}" > /dev/null 2>&1; then
        printf '  %-10s %s uid missing (nothing provisioned under this name)\n' '' "${BAD}"
        return 0
    fi
    if [ ! -f "${SOCKET_DEST}" ]; then
        socket="${DEFER} deferred"
        service="${DEFER} deferred"
        shell="${DEFER} deferred"
    else
        if systemctl is-active --quiet "euler-user@${slug}.socket" 2>/dev/null; then
            socket="${OK} listening"
        else
            socket="${BAD} inactive"
        fi
        # Not running is NORMAL, not a fault: the socket activates the instance on the
        # first request and the reaper/logout tears it down again, so an idle
        # collaborator legitimately has no process — hence '…', not '✗'.
        if systemctl is-active --quiet "euler-user@${slug}.service" 2>/dev/null; then
            service="${OK} running"
            shell="$(shell_state "${slug}")"
        else
            service="${DEFER} idle (socket-activated on demand)"
            shell="${DEFER} none (instance idle)"
        fi
    fi
    # The clone and its hooks live under a 0700 home — only root can see them (as vikas the
    # test silently reads "absent", which is exactly how "no-clone" got misreported).
    printf '  %-10s uid %s · clone %s · hooks %s · socket %s · service %s\n' '' \
        "${OK}" \
        "$(check_mark sudo test -d "${clone}/.git")" \
        "$(check_mark sudo test -x "${clone}/.git/hooks/pre-commit" -a -x "${clone}/.git/hooks/pre-push")" \
        "${socket}" \
        "${service}"
    printf '  %-10s web shell %s\n' '' "${shell}"
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
    purge-legacy) do_purge_legacy ;;
    status)      do_status "$@" ;;
    -h | --help | help) usage ;;
    *) echo "Unknown action: ${ACTION}"; usage; exit 1 ;;
esac

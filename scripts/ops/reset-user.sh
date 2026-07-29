#!/usr/bin/env bash
# Reset one collaborator's clone to origin/master — the operator's repair of last resort.
#
#   sudo bash scripts/ops/reset-user.sh <slug> [--dry-run] [--yes] [--no-filter]
#
# Runs, as the collaborator, the two commands that make their clone match the remote
# exactly:
#
#     git fetch --prune origin
#     git reset --hard origin/master
#
# **This discards their local commits and every uncommitted change.** That is the point —
# it is for a clone wedged in a state its owner cannot get out of with the verbs their
# profile has (a reader has no `git-reset` and no `!`), which is precisely when someone
# else has to reach in. It is not a routine sync: `git-sync` is, and it preserves work.
# So the state about to be destroyed is printed first and confirmed, unless --yes.
#
# Why run it as them rather than as root: git writes objects, the index and the worktree.
# Doing that as root leaves root-owned files in a home the collaborator's own uid then
# cannot write, which converts one wedged clone into a permanently wedged one.
#
# The smudge filter and the vault: `reset --hard` checks out solutions/private, which the
# clean/smudge filter must decrypt, which needs the user's master key — and their private
# key may be vault-encrypted, unlocked only inside their own session. A `sudo -u` shell has
# no such session, so the reset can fail on decryption alone. --no-filter is the way through
# that: reset with the filter not required, leaving solutions/private as **ciphertext** in a
# structurally correct clone, which their own `git-filter install` then decrypts in place.
#
# Egress: the host is default-deny outbound and the Squid allowlist is the only way to
# github.com. The per-user services get that wiring from /etc/euler/egress.env via
# EnvironmentFile=, but a `sudo -u` shell inherits nothing, so a bare fetch here fails at
# DNS ("Could not resolve host: github.com") rather than at the network. This script passes
# the same env through explicitly — see docs/web-server-guide.md § Egress.
#
# Author: Vikas Munshi <vikas.munshi@gmail.com>
# Copyright (c) 2026. All rights reserved.
# Licensed under the MIT License.
set -uo pipefail

SLUG=''
DRY_RUN=0
ASSUME_YES=0
NO_FILTER=0

usage() {
    cat <<USAGE
Usage: sudo bash $0 <slug> [--dry-run] [--yes] [--no-filter]

  <slug>        the collaborator's system slug (their uid / home / branch name)
  --dry-run     print the commands instead of running them
  --yes         skip the confirmation (for scripted repairs)
  --no-filter   reset with the crypt filter not required — solutions/private stays
                ciphertext, and their own \`git-filter install\` decrypts it later.
                Use when the reset fails because the vault is locked outside their session.

Discards local commits AND uncommitted changes in /home/<slug>/euler. See \`git-sync\`
for the routine, work-preserving pull.
USAGE
}

for arg in "$@"; do
    case "${arg}" in
        --dry-run) DRY_RUN=1 ;;
        --yes | -y) ASSUME_YES=1 ;;
        --no-filter) NO_FILTER=1 ;;
        -h | --help | help) usage; exit 0 ;;
        -*) echo "Error: unknown option: ${arg}" >&2; usage >&2; exit 2 ;;
        *)
            if [[ -n "${SLUG}" ]]; then
                echo "Error: one slug at a time (got '${SLUG}' and '${arg}')" >&2
                exit 2
            fi
            SLUG="${arg}"
            ;;
    esac
done

if [[ -z "${SLUG}" ]]; then usage >&2; exit 2; fi
if [[ ${EUID} -ne 0 ]]; then
    echo "Error: run under sudo — this acts on another user's home." >&2
    exit 1
fi
if ! id -u "${SLUG}" &> /dev/null; then
    echo "Error: no such user: ${SLUG}" >&2
    exit 1
fi

HOME_DIR="$(getent passwd "${SLUG}" | cut -d: -f6)"
CLONE="${HOME_DIR}/euler"
if [[ ! -d "${CLONE}/.git" ]]; then
    echo "Error: no clone at ${CLONE}" >&2
    exit 1
fi

# The proxy wiring the services get from EnvironmentFile= and a sudo shell does not.
# Passed as an explicit `env` prefix rather than exported: sudo resets the environment
# (env_reset), so an export here would simply be dropped.
EGRESS_ENV='/etc/euler/egress.env'
PROXY_ENV=()
if [[ -r "${EGRESS_ENV}" ]]; then
    while IFS= read -r line; do
        if [[ "${line}" =~ ^[A-Za-z_][A-Za-z0-9_]*= ]]; then PROXY_ENV+=("${line}"); fi
    done < "${EGRESS_ENV}"
fi
# …and the one variable that tells the crypt filter WHICH clone it is filtering. The
# per-user services set it; a sudo shell has nothing, and the filter then has to guess from
# its own cwd. It guesses correctly (git runs a filter at the top of the worktree), but
# saying it outright costs nothing and is what every other caller does.
PROXY_ENV+=("EULER_REPO_ROOT=${CLONE}")

# as_user — run git in their clone, as them. Never as root (see the header).
as_user() {
    sudo -u "${SLUG}" env ${PROXY_ENV[@]+"${PROXY_ENV[@]}"} git -C "${CLONE}" "$@"
}

# run_step — execute, or print under --dry-run.
run_step() {
    if [[ ${DRY_RUN} -eq 1 ]]; then
        echo "  [dry-run] sudo -u ${SLUG} env ${PROXY_ENV[*]+${#PROXY_ENV[@]} proxy var(s)} " \
             "git -C ${CLONE} $*"
        return 0
    fi
    as_user "$@"
}

echo "── ${SLUG} — ${CLONE}"
branch="$(as_user rev-parse --abbrev-ref HEAD 2> /dev/null || echo '(unknown)')"
dirty_count="$(as_user --no-optional-locks status --porcelain 2> /dev/null | wc -l)"
stash_count="$(as_user stash list 2> /dev/null | wc -l)"
unpushed="$(as_user log --oneline origin/master..HEAD 2> /dev/null | wc -l)"
echo "   branch          : ${branch}"
echo "   uncommitted     : ${dirty_count} file(s)   <- will be DISCARDED"
echo "   commits not on origin/master: ${unpushed}  <- will be DISCARDED"
echo "   stash entries   : ${stash_count} (untouched by this script)"

if [[ ${DRY_RUN} -ne 1 && ${ASSUME_YES} -ne 1 ]]; then
    read -r -p "Reset ${SLUG}'s clone to origin/master, discarding the above? [y/N] " reply
    if [[ ! "${reply}" =~ ^[Yy]$ ]]; then
        echo "   nothing done"
        exit 0
    fi
fi

echo "   fetching..."
if ! run_step fetch --prune origin; then
    echo "Error: fetch failed." >&2
    if [[ ${#PROXY_ENV[@]} -eq 0 ]]; then
        echo "  No proxy env found at ${EGRESS_ENV}: on a host whose egress is default-deny," >&2
        echo "  git cannot even resolve github.com from here. Check the egress kit." >&2
    else
        echo "  The egress proxy env was passed through; check euler-proxy.service and the" >&2
        echo "  allowlist (scripts/setup/egress.sh status), then this user's git remote." >&2
    fi
    exit 1
fi

echo "   resetting to origin/master..."
if [[ ${NO_FILTER} -eq 1 ]]; then
    # `required=false` makes git keep a blob the filter refused, rather than failing the
    # checkout: solutions/private lands as ciphertext and the clone is otherwise correct.
    run_step -c filter.solver-crypt.required=false reset --hard origin/master
else
    run_step reset --hard origin/master
fi
rc=$?

if [[ ${rc} -ne 0 ]]; then
    echo >&2
    echo "Error: reset failed (${rc})." >&2
    echo "  If it failed decrypting solutions/private, the vault is locked outside their" >&2
    echo "  session — re-run with --no-filter, then have them run \`git-filter install\`" >&2
    echo "  in their own shell to decrypt in place." >&2
    exit "${rc}"
fi

if [[ ${DRY_RUN} -eq 1 ]]; then
    echo "   [dry-run] nothing was changed"
    exit 0
fi

echo "   now at: $(as_user log --oneline -1 2> /dev/null)"
left="$(as_user --no-optional-locks status --porcelain 2> /dev/null | wc -l)"
echo "   uncommitted after reset: ${left}"
if [[ ${NO_FILTER} -eq 1 ]]; then
    echo "   NOTE: solutions/private is ciphertext — they must run \`git-filter install\`."
fi
echo "   Have them reconnect their web shell before testing (read_master_key is cached)."

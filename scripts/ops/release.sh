#!/usr/bin/env bash
# Cut a new version and ship it — the whole release turnaround, in one command.
#
#   bash scripts/ops/release.sh [--dry-run] [--yes] [--skip-updates]
#                               [--no-deploy] [--no-follow] [--no-tmux] [--log FILE]
#
# The release flow is four steps that are always run in the same order and are easy to run
# out of order (or to stop half-way through) by hand:
#
#   1. regenerate everything that is machine-maintained, so the release commit describes
#      the software that actually exists — `update-models`, `update-usd-rate`,
#      `update-tags`, `update-docs`, in that order (see "Why that order" below);
#   2. `make release`  — derive the SemVer bump from the Conventional Commits since the
#      last tag, rewrite solver/version.py, commit, tag vX.Y.Z, push commit + tag.
#      **Skipped, not fatal, when there is nothing to release**: an unchanged tree since
#      the last tag has no bump to make, and `release.sh` exits 1 on it. That is not a
#      reason to abandon the run — re-shipping the build that is already tagged is a
#      perfectly ordinary thing to want — so the bump is skipped and steps 3 and 4 go
#      ahead with the current version;
#   3. `make redeploy-web` — rebuild the /opt/euler venv from the pushed release and
#      bounce the services onto it (gated on `make check-version`, which is exactly the
#      tag step 2 just published);
#   4. `make status-web`  — the read-only sweep that says whether the stack came back.
#
# Why that order for the update verbs: each one lands its own commit, and `update-docs`
# regenerates the command catalogue from the **live registry**, where a command's usage
# quotes the `Model` enum (`[model=claude-opus-5|…]`). So `update-models` has to rewrite
# the enum *before* the docs are generated from it, or the catalogue ships a model list
# that was already stale when it was written. `update-usd-rate` and `update-tags` are
# independent of the docs, but they are cheap and they commit — running them first keeps
# the release commit at the top of a fully reconciled tree.
#
# ── Steps 3 and 4 are detached, and everything is logged ──────────────────────────────
#
# `redeploy-web` bounces the per-user instances, which **drops every live web shell** —
# including, if this is being run from one, the terminal running this script. Anything
# still to do after that point (the rest of `redeploy-web`, then the status sweep) would
# die with it, half-deployed. So steps 3 and 4 are written to a temporary script and
# launched under `nohup` with stdin on /dev/null, ignoring INT/QUIT/HUP: once step 3
# starts, closing the terminal, losing the ssh connection or pressing Ctrl-C stops the
# *watching*, not the deploy. Kill it deliberately with `kill <pid>` (TERM is not
# trapped); the pid is printed and logged.
#
# `nohup` rather than `setsid`, deliberately: sudo's timestamps are tty-keyed, so a child
# in a brand-new session with no controlling terminal would no longer match the ticket this
# script primes, and would fail its first sudo with "a terminal is required to
# authenticate". Staying in the session keeps the ticket usable.
#
# ── …and the whole run happens inside tmux ────────────────────────────────────────────
#
# The detach above survives the *script* dying, but not the terminal being **destroyed**:
# when an ssh connection drops, the pty goes with it, and a tty-bound sudo ticket dies at
# the same moment. Every sudo call after that has nothing to authenticate against and no
# terminal to ask on. This host runs sudo-rs (0.2.x), which does not offer sudo 1.9's
# `timestamp_type` knob, so the ticket cannot simply be unbound from the tty.
#
# So the script re-runs itself inside a tmux session (`euler-release`) and does the real
# work there. tmux's server lives outside the login session and keeps the pane's pty open
# across a disconnect, so the ticket stays valid and the release runs to completion whether
# or not anyone is attached. Detach deliberately with Ctrl-b d; come back with
# `tmux attach -t euler-release`; read it from anywhere with `tail -f` on the log. The
# re-run carries `--no-tmux` (that is what stops it recursing), and the release's exit
# status is handed back through a temp file, since tmux only ever reports its own.
#
# It is skipped where it would buy nothing: `--dry-run`, `--no-deploy`, `--no-follow`, no
# terminal at all (cron/CI), already inside tmux, or `--no-tmux`. A host without tmux gets
# a note and an inline run — everything still works there except surviving a disconnect.
# The one thing nothing in userland survives is the session's cgroup being killed outright
# (`systemctl stop` on a euler-user@ instance, say). If you are deploying *from* a web
# shell, expect to finish the tail of the run from a real terminal.
#
# The whole run — this script's own output and the detached steps' — is appended to one
# log file, printed at the start and named again at the end. While the terminal lives the
# detached output is also followed on screen, so an attended run looks like an ordinary one.
#
# Preconditions this script insists on, up front, before it changes anything:
#
#   * a **clean working tree** — `make release` refuses on a dirty tree anyway, but it
#     refuses *after* four regenerating verbs have already committed. Checked with
#     `git status --porcelain`, never `git diff`: the transparent encryption filter
#     re-encrypts solutions/private/** on every read, so `git diff` reports phantom churn
#     on a clean tree. (If `git status` itself errors with `gitfilter: cannot load master
#     key`, that is the vault being locked, not a dirty tree — unlock and re-run.)
#   * **sudo** — steps 3 and 4 shell out to the systemd kits, which sudo internally. This
#     script validates sudo first (prompting once, here, where a terminal exists) and then
#     keeps the timestamp warm — in this shell for the length of steps 1 and 2, and from
#     inside the detached job for steps 3 and 4 — so a password prompt never lands in the
#     middle of a redeploy that has already stopped the services.
#
# Nothing here is unattended: the plan is printed and confirmed before the first write.
# After the confirmation it runs to the end or stops at the first failing step, leaving
# the completed steps in place — every one of them is idempotent, so the fix is to clear
# whatever failed and run it again.
#
# Author: Vikas Munshi <vikas.munshi@gmail.com>
# Copyright (c) 2026. All rights reserved.
# Licensed under the MIT License.
set -uo pipefail

DRY_RUN=0
ASSUME_YES=0
SKIP_UPDATES=0
NO_DEPLOY=0
NO_FOLLOW=0
NO_TMUX=0
LOG=''
KEEPALIVE_PID=''
DEPLOY_PID=''

# The arguments exactly as given, kept for the re-exec into tmux below.
ORIG_ARGS=("$@")
# The tmux session a release runs in. Fixed, not per-run: a second release starting while
# one is in flight is a mistake, and a name that is always the same both catches that and
# gives `tmux attach -t euler-release` something to remember.
TMUX_SESSION='euler-release'

# The regenerating verbs, in the order step 1 runs them. Each is a solver command that
# commits its own output (`chore(<verb>): …`) and is a no-op on an already-current tree.
UPDATE_VERBS=(update-models update-usd-rate update-tags update-docs)

usage() {
    cat <<USAGE
Usage: bash $0 [--dry-run] [--yes] [--skip-updates] [--no-deploy] [--no-follow] [--log FILE]

  --dry-run        print every step instead of running it, and preview the version bump
                   via 'make release ARGS=--dry-run'. Touches nothing, needs no sudo.
  --yes, -y        skip the confirmation prompt (for a scripted release).
  --skip-updates   go straight to the release; do not run the update-* verbs. Use when
                   they have just been run, or when the host cannot reach the Anthropic
                   API / the ECB feed and the catalogue is known to be current.
  --no-deploy      stop after 'make release' — bump, tag and push, but do not touch the
                   web stack. Ship it later with 'make redeploy-web'.
  --no-follow      launch the detached deploy and return immediately, instead of
                   following its output until it finishes. The log has everything.
                   Implies --no-tmux: there is nothing left to hold a session open.
  --no-tmux        run in this terminal instead of re-running inside a tmux session.
                   The deploy then dies with the terminal's pty, taking the sudo
                   ticket with it — see the header.
  --log FILE       append the run's output here (default: a timestamped file under
                   \${TMPDIR:-/tmp}).

Runs, in order: solver ${UPDATE_VERBS[*]} -> make release -> make redeploy-web
-> make status-web. Needs a clean working tree, an unlocked vault, and sudo.

With nothing to release (no commits since the last tag) the bump is skipped rather than
fatal, and the run goes straight on to re-deploy the build that is already tagged.

The run happens inside the tmux session '${TMUX_SESSION}' (Ctrl-b d to detach, 'tmux
attach -t ${TMUX_SESSION}' to return), so a dropped connection costs neither the deploy
nor the sudo ticket. Steps 3 and 4 additionally run detached, so they survive the web
shell that 'redeploy-web' itself drops.
USAGE
}

while [[ $# -gt 0 ]]; do
    case "${1}" in
        --dry-run) DRY_RUN=1 ;;
        --yes | -y) ASSUME_YES=1 ;;
        --skip-updates) SKIP_UPDATES=1 ;;
        --no-deploy) NO_DEPLOY=1 ;;
        --no-follow) NO_FOLLOW=1 ;;
        --no-tmux) NO_TMUX=1 ;;
        --log)
            shift
            [[ $# -gt 0 ]] || { echo "Error: --log needs a file path" >&2; exit 2; }
            LOG="${1}"
            ;;
        --log=*) LOG="${1#--log=}" ;;
        -h | --help | help) usage; exit 0 ;;
        *) echo "Error: unknown option: ${1}" >&2; usage >&2; exit 2 ;;
    esac
    shift
done

# ── plumbing ──────────────────────────────────────────────────────────────────────────

say()   { printf '%s\n' "$*"; }
head2() { printf '\n── %s\n' "$*"; }
fail()  { printf 'Error: %s\n' "$*" >&2; exit 1; }

# run_step — announce and execute one command, or print it under --dry-run. Returns the
# command's own status; every caller checks it, since the whole point of the script is
# that a failing step stops the ones after it.
run_step() {
    if [[ ${DRY_RUN} -eq 1 ]]; then
        printf '   [dry-run] %s\n' "$*"
        return 0
    fi
    printf '   $ %s\n' "$*"
    "$@"
}

# has_tty — is there a controlling terminal that can actually be written to? Tested by
# opening it, not with `[ -e /dev/tty ]`: the device node exists for every process, and a
# process without a controlling terminal (a cron job, a CI runner) only finds that out on
# open, with ENXIO.
has_tty() { { : > /dev/tty; } 2> /dev/null; }

# confirm — ask on the terminal itself. Stdout is a pipe into `tee` by the time this runs,
# and a prompt without a newline can sit in that pipe unseen; /dev/tty goes straight to
# the screen. The answer is echoed so the log records what was agreed to.
confirm() {
    local prompt="$1" reply=''
    if has_tty; then
        printf '%s' "${prompt}" > /dev/tty
        read -r reply < /dev/tty
    else
        read -r -p "${prompt}" reply
    fi
    say "${prompt}${reply}"
    [[ "${reply}" =~ ^[Yy]$ ]]
}

# Kill the sudo keep-alive whatever way we leave. The detached deploy is NOT cleaned up
# here — outliving this shell is its entire purpose.
# shellcheck disable=SC2329  # invoked indirectly, by the trap below
cleanup() {
    if [[ -n "${KEEPALIVE_PID}" ]]; then kill "${KEEPALIVE_PID}" 2> /dev/null; fi
}
trap cleanup EXIT TERM

# Ctrl-C while following the detached deploy stops the following, not the deploy.
# shellcheck disable=SC2329  # invoked indirectly, by the trap below
on_int() {
    if [[ -n "${DEPLOY_PID}" ]] && kill -0 "${DEPLOY_PID}" 2> /dev/null; then
        say ""
        say "   (stopped watching — the deploy is still running as pid ${DEPLOY_PID};"
        say "    follow it with: tail -f ${LOG}    stop it with: kill ${DEPLOY_PID})"
        exit 0
    fi
    say ""
    fail "interrupted."
}
trap on_int INT

# The tracked version number — the single source of truth, read the same way
# `make check-version` reads it.
read_version() {
    sed -nE "s/^__version__ = '([^']*)'.*/\1/p" solver/version.py
}

# ── preflight ─────────────────────────────────────────────────────────────────────────

ROOT="$(git rev-parse --show-toplevel 2> /dev/null)"
[[ -n "${ROOT}" ]] || fail "not inside a git repository."
cd "${ROOT}" || fail "cannot cd to ${ROOT}"
[[ -f solver/version.py ]] || fail "${ROOT} is not the solver checkout (no solver/version.py)."

command -v git  > /dev/null || fail "git is not on PATH."
command -v make > /dev/null || fail "make is not on PATH."
if [[ ${SKIP_UPDATES} -eq 0 ]]; then
    command -v solver > /dev/null \
        || fail "solver is not on PATH — activate the venv (or 'make install-all'), or pass --skip-updates."
fi

# Clean tree, via status (see the header on why not `git diff`). The command's own
# failure is reported separately: that is usually the locked vault, not a dirty tree.
if ! dirty="$(git status --porcelain 2>&1)"; then
    say "${dirty}"
    fail "'git status' failed. If it complains about the master key, the vault is locked —
       unlock it in this terminal and run this script again."
fi
if [[ -n "${dirty}" ]]; then
    say "${dirty}"
    fail "working tree is not clean — commit or stash the above, then release."
fi

BRANCH="$(git rev-parse --abbrev-ref HEAD 2> /dev/null || echo '(unknown)')"
LAST_TAG="$(git describe --tags --abbrev=0 --match 'v*' 2> /dev/null || echo 'none')"
CURRENT="$(read_version)"
[[ -n "${CURRENT}" ]] || fail "cannot read __version__ from solver/version.py."

# The log is named before the tmux hand-off below, so both sides of it write to one file.
if [[ ${DRY_RUN} -eq 0 ]]; then
    [[ -n "${LOG}" ]] || LOG="${TMPDIR:-/tmp}/euler-new-version-$(date -u +%Y%m%d-%H%M%S).log"
    mkdir -p "$(dirname "${LOG}")" 2> /dev/null
    : >> "${LOG}" || fail "cannot write the log file ${LOG}"
fi

# ── run the whole thing inside tmux ───────────────────────────────────────────────────
#
# tmux owns the pty, and it is a server process outside this login session — so when the
# ssh connection drops, the pane's terminal does NOT die. That is the one thing that makes
# the sudo ticket survive a disconnect (it is bound to the tty, and this host's sudo-rs
# offers no `timestamp_type` knob to unbind it), and it is why the whole script re-runs
# itself in a session rather than only detaching steps 3 and 4. Disconnected, the release
# keeps running; `tmux attach -t euler-release` picks the screen back up mid-flight.
#
# The re-exec is skipped when there is nothing long-running to protect (--dry-run,
# --no-deploy), when the caller does not intend to wait anyway (--no-follow), when there
# is no terminal to attach to (a cron/CI run — tmux would just fail to open one), and of
# course when this IS the re-run, which arrives with --no-tmux. Missing tmux is a note,
# not a failure: the nohup detach still covers everything except the ticket.
if [[ ${DRY_RUN} -eq 0 && ${NO_DEPLOY} -eq 0 && ${NO_FOLLOW} -eq 0 && ${NO_TMUX} -eq 0 && -z "${TMUX:-}" ]]; then
    if ! command -v tmux > /dev/null; then
        say "note: tmux is not installed — running in this terminal. A disconnect will cost"
        say "      the sudo ticket mid-deploy; 'sudo apt install tmux' buys that back."
    elif ! has_tty; then
        : # no terminal to attach a session to — run inline, the detach still applies
    elif tmux has-session -t "${TMUX_SESSION}" 2> /dev/null; then
        fail "a tmux session named '${TMUX_SESSION}' is already running — a release may be in
       flight. Look with 'tmux attach -t ${TMUX_SESSION}', and if it is finished,
       'tmux kill-session -t ${TMUX_SESSION}' before starting another."
    else
        # Single-quote every argument by hand rather than with printf %q: tmux hands the
        # command line to /bin/sh, and %q emits bash-only $'…' forms for anything awkward.
        sq() { printf "'%s'" "${1//\'/\'\\\'\'}"; }
        RC_FILE="$(mktemp "${TMPDIR:-/tmp}/euler-new-version-rc-XXXXXX")"
        inner="bash $(sq "$(cd "$(dirname "$0")" && pwd)/$(basename "$0")")"
        for arg in ${ORIG_ARGS[@]+"${ORIG_ARGS[@]}"}; do inner+=" $(sq "${arg}")"; done
        inner+=" --no-tmux --log $(sq "${LOG}")"
        # The status the release exits with has to survive the session: tmux reports its
        # own, never the command's.
        inner+="; printf '%s' \$? > $(sq "${RC_FILE}")"

        say "Running the release inside tmux session '${TMUX_SESSION}'."
        say "  detach and leave it running : Ctrl-b d"
        say "  come back to it             : tmux attach -t ${TMUX_SESSION}"
        say "  read it from anywhere       : tail -f ${LOG}"
        say ""
        tmux new-session -s "${TMUX_SESSION}" -c "${ROOT}" "${inner}"
        rc="$(cat "${RC_FILE}" 2> /dev/null)"
        rm -f "${RC_FILE}"
        if [[ -z "${rc}" ]]; then
            # No status file: the session was killed, or is still alive because the pane
            # was detached rather than finished. Both are ordinary, and neither is this
            # shell's to report on.
            if tmux has-session -t "${TMUX_SESSION}" 2> /dev/null; then
                say "Detached — the release is still running in '${TMUX_SESSION}'."
                say "  tmux attach -t ${TMUX_SESSION}     tail -f ${LOG}"
                exit 0
            fi
            fail "the tmux session ended without reporting a status — read ${LOG}."
        fi
        exit "${rc}"
    fi
fi

# One log for the whole run: this shell tees into it, and the detached steps append to the
# same file, so the record is complete whether or not anyone was watching at the end.
# A dry run writes nothing anywhere, log included.
if [[ ${DRY_RUN} -eq 0 ]]; then
    exec > >(tee -a "${LOG}") 2>&1
fi

# Sudo: prompt here, once, while there is a terminal to prompt on — and keep the timestamp
# warm for the rest of steps 1 and 2 so the detached job inherits a valid ticket rather
# than meeting a prompt it cannot answer. Skipped when there is nothing to deploy.
if [[ ${DRY_RUN} -eq 0 && ${NO_DEPLOY} -eq 0 ]]; then
    command -v sudo > /dev/null || fail "sudo is not installed — the web stack cannot be redeployed without it."
    say "The web steps need sudo; authenticating now so no prompt interrupts the redeploy."
    sudo -v || fail "sudo authentication failed — this user cannot deploy the web stack.
       Re-run with --no-deploy to bump, tag and push only."
    # Refresh every 50s (the timestamp lives 15m by default, but a long update-tags run can
    # outlast a stale one), and stop when this shell is gone.
    while true; do
        sleep 50
        kill -0 "$$" 2> /dev/null || exit 0
        sudo -n true 2> /dev/null || exit 0
    done &
    KEEPALIVE_PID=$!
fi

# ── the plan ──────────────────────────────────────────────────────────────────────────

say ""
say "══ new version ══════════════════════════════════════════════════════════════"
say "   repository      : ${ROOT}"
say "   branch          : ${BRANCH}"
say "   HEAD            : $(git log --oneline -1 2> /dev/null)"
say "   last release    : ${LAST_TAG}   (solver/version.py: ${CURRENT})"
say "   unreleased      : $(git rev-list --count "$([[ ${LAST_TAG} == none ]] && echo HEAD || echo "${LAST_TAG}..HEAD")" 2> /dev/null || echo '?') commit(s)"
[[ -n "${LOG}" ]] && say "   log             : ${LOG}"
say ""
say "   will run:"
if [[ ${SKIP_UPDATES} -eq 1 ]]; then
    say "     1. (skipped) the update-* verbs"
else
    say "     1. solver ${UPDATE_VERBS[*]}      <- each commits its own output"
fi
if [[ "${LAST_TAG}" != 'none' && -z "$(git rev-list "${LAST_TAG}..HEAD" 2> /dev/null)" ]]; then
    say "     2. make release                             <- nothing new since ${LAST_TAG}: skipped unless step 1 commits"
else
    say "     2. make release                             <- bump + commit + tag + PUSH to origin"
fi
if [[ ${NO_DEPLOY} -eq 1 ]]; then
    say "     3. (skipped) make redeploy-web"
    say "     4. (skipped) make status-web"
else
    say "     3. make redeploy-web  [detached]            <- rebuild /opt/euler, bounce services (drops live web shells)"
    say "     4. make status-web    [detached]            <- read-only sweep of the stack"
    say ""
    say "   Steps 3 and 4 run under nohup: once step 3 starts, this terminal can go away"
    say "   without taking the deploy with it."
fi
say ""

if [[ ${DRY_RUN} -eq 0 && ${ASSUME_YES} -eq 0 ]]; then
    if ! confirm "Proceed? [y/N] "; then
        say "   nothing done"
        exit 0
    fi
fi

# ── 1. regenerate what is machine-maintained ──────────────────────────────────────────

if [[ ${SKIP_UPDATES} -eq 1 ]]; then
    head2 "1. update-* — skipped (--skip-updates)"
else
    for verb in "${UPDATE_VERBS[@]}"; do
        head2 "1. ${verb}"
        # One solver invocation per verb rather than one command block: the block would
        # need '&&' to stop at a failure, and this way the failing verb names itself.
        if ! run_step solver "${verb}"; then
            fail "${verb} failed — nothing has been released. Fix it and re-run;
       the verbs already committed above are idempotent."
        fi
    done

    # The verbs commit their own output, so a dirty tree here means one of them wrote
    # files and its commit was rejected (a hook, most likely). `make release` would fail
    # on it next, less clearly.
    if [[ ${DRY_RUN} -eq 0 ]]; then
        leftover="$(git status --porcelain 2>&1)"
        if [[ -n "${leftover}" ]]; then
            say "${leftover}"
            fail "the update verbs left the tree dirty — a regeneration was written but not
       committed. Commit (or discard) the above, then re-run."
        fi
    fi
fi

# ── 2. cut the release ────────────────────────────────────────────────────────────────

head2 "2. make release"

# Nothing new since the tag is not a failure — it is a release that would have no content,
# and release.sh exits 1 on exactly that. Skip the bump instead of aborting the run: the
# tree already *is* a released version, so steps 3 and 4 can ship it as it stands. (Checked
# here, after step 1: an update verb committing is precisely what turns "nothing to
# release" into something to release.)
NOTHING_NEW=0
if [[ "${LAST_TAG}" != 'none' && -z "$(git rev-list "${LAST_TAG}..HEAD" 2> /dev/null)" ]]; then
    NOTHING_NEW=1
    say "   no commits since ${LAST_TAG} — the tree is already the released version."
    if [[ ${NO_DEPLOY} -eq 1 ]]; then
        say "   Nothing to release, and --no-deploy stops before the redeploy: nothing to do."
    else
        say "   Skipping the bump; steps 3 and 4 re-ship the current build (v${CURRENT})."
    fi
fi

if [[ ${NOTHING_NEW} -eq 1 ]]; then
    : # no bump to make — RELEASED below is the version already on disk and on origin
elif [[ ${DRY_RUN} -eq 1 ]]; then
    say "   previewing the bump (writes nothing):"
    preview="$(make release ARGS=--dry-run)" || fail "'make release --dry-run' failed."
    say "   ${preview}"
    # release.sh's preview line reads '[dry-run] vA.B.C -> vX.Y.Z (…)'; the arrow's right
    # side is the number the rest of this run would be about, so the steps below name it
    # rather than the version still on disk.
    PREVIEWED="$(sed -nE 's/.*-> v([0-9]+\.[0-9]+\.[0-9]+).*/\1/p' <<< "${preview}")"
else
    if ! run_step make release; then
        fail "'make release' failed — see above. Nothing was deployed.
       If it bumped and tagged but the push failed, publish with:
         git push origin HEAD v\$(sed -nE \"s/^__version__ = '([^']*)'.*/\\1/p\" solver/version.py)"
    fi
fi

RELEASED="$(read_version)"
[[ ${DRY_RUN} -eq 1 && -n "${PREVIEWED:-}" ]] && RELEASED="${PREVIEWED}"

# ── 3 & 4. ship it, detached ──────────────────────────────────────────────────────────

if [[ ${NO_DEPLOY} -eq 1 ]]; then
    head2 "3. make redeploy-web — skipped (--no-deploy)"
    say ""
    if [[ ${DRY_RUN} -eq 1 ]]; then
        if [[ ${NOTHING_NEW} -eq 1 ]]; then
            say "✓ dry run complete — nothing was changed. A real run would do nothing at all:"
            say "  no commits to release, and --no-deploy stops before the redeploy."
        else
            say "✓ dry run complete — nothing was changed. A real run would stop with v${RELEASED}"
            say "  released and pushed, and the host still on the previous build."
        fi
        exit 0
    fi
    if [[ ${NOTHING_NEW} -eq 1 ]]; then
        say "✓ nothing to release — v${RELEASED} is already tagged and pushed, and nothing was deployed."
    else
        say "✓ v${RELEASED} is released and pushed; the deployed venv still runs the previous build."
    fi
    say "  Ship it with: make redeploy-web"
    say "  log: ${LOG}"
    exit 0
fi

if [[ ${DRY_RUN} -eq 1 ]]; then
    head2 "3. make redeploy-web   [would be detached under nohup, appending to the log]"
    say "   [dry-run] make redeploy-web"
    head2 "4. make status-web     [same detached job]"
    say "   [dry-run] make status-web"
    say ""
    say "✓ dry run complete — nothing was changed."
    exit 0
fi

# The two steps are written out as a script and run from a file rather than piped in on
# stdin: a heredoc on stdin *is* the child's stdin, and anything inside that reads stdin
# would swallow the rest of the script. From a file, stdin is free to be /dev/null — which
# is what a detached job with nobody to answer a prompt should have.
STEPS="$(mktemp "${TMPDIR:-/tmp}/euler-new-version-steps-XXXXXX.sh")" \
    || fail "cannot create the detached step script."

cat > "${STEPS}" <<'STEPS_EOF'
#!/usr/bin/env bash
# Steps 3 and 4 of scripts/ops/release.sh, detached from the terminal that
# started them. Generated per run and deleted on exit — do not edit; edit the parent.
set -uo pipefail

# The deploy must outlive the terminal, and the terminal's death is announced with HUP —
# INT and QUIT because a Ctrl-C in the watching shell reaches this process group too.
# TERM is deliberately left alone: `kill <pid>` is how a deploy is called off on purpose.
trap '' INT QUIT HUP

cd "${EULER_ROOT}" || exit 1

# The parent primed sudo while it still had a terminal to prompt on; from here the ticket
# has to stay warm on its own, since a venv rebuild plus a status sweep can outlast one
# timestamp. If the ticket is already gone there is nothing to keep alive — say so, since
# the first sudo call is then going to fail with no way to ask.
keepalive_pid=''
if sudo -n true 2> /dev/null; then
    while true; do
        sleep 50
        kill -0 "$$" 2> /dev/null || exit 0
        sudo -n true 2> /dev/null || exit 0
    done &
    keepalive_pid=$!
else
    printf 'warning: no usable sudo ticket in the detached job — the deploy will fail if\n'
    printf '         it is asked for a password. Re-run "make redeploy-web" by hand.\n'
fi

cleanup() {
    if [[ -n "${keepalive_pid}" ]]; then kill "${keepalive_pid}" 2> /dev/null; fi
    rm -f "$0"
}
trap cleanup EXIT

# Whether step 2 actually cut a release changes only what these lines are allowed to claim.
if [[ "${EULER_NOTHING_NEW:-0}" == '1' ]]; then
    release_note="v${EULER_RELEASED} was already released and pushed (there was nothing to bump)"
else
    release_note="v${EULER_RELEASED} IS released and pushed"
fi

printf '\n── 3. make redeploy-web   (detached, pid %s)\n' "$$"
printf '   (check-version first: v%s must be on origin. Live web shells are dropped.)\n' "${EULER_RELEASED}"
printf '   $ make redeploy-web\n'
if ! make redeploy-web; then
    printf '\nError: %s\n' "'make redeploy-web' failed — ${release_note},
       but the host still runs the previous build. Re-run 'make redeploy-web' once the
       cause is fixed; 'make status-web' shows what is up in the meantime."
    exit 1
fi

printf '\n── 4. make status-web\n'
printf '   $ make status-web\n'
make status-web || printf '   (status sweep reported a problem — read the sections above)\n'

if [[ "${EULER_NOTHING_NEW:-0}" == '1' ]]; then
    printf '\n✓ v%s (nothing new to release) re-deployed.\n' "${EULER_RELEASED}"
else
    printf '\n✓ v%s released, pushed, and deployed.\n' "${EULER_RELEASED}"
fi
printf '  Collaborators pick it up with '"'"'git-sync'"'"'; a new shell command also needs them to\n'
printf '  reconnect their web terminal (the PTY builds its registry at spawn).\n'
STEPS_EOF

EULER_ROOT="${ROOT}" EULER_RELEASED="${RELEASED}" EULER_NOTHING_NEW="${NOTHING_NEW}" \
    nohup bash "${STEPS}" < /dev/null >> "${LOG}" 2>&1 &
DEPLOY_PID=$!

head2 "3 & 4. detached (pid ${DEPLOY_PID})"
say "   This terminal is no longer load-bearing: the deploy continues if it goes away."
say "   follow: tail -f ${LOG}      stop: kill ${DEPLOY_PID}"

if [[ ${NO_FOLLOW} -eq 1 ]]; then
    say ""
    if [[ ${NOTHING_NEW} -eq 1 ]]; then
        say "✓ nothing to release; v${RELEASED} is being re-deployed as pid ${DEPLOY_PID}."
    else
        say "✓ v${RELEASED} released and pushed; the deploy is running as pid ${DEPLOY_PID}."
    fi
    say "  log: ${LOG}"
    exit 0
fi

# Follow the detached output on the terminal directly — NOT through this shell's stdout,
# which is a pipe into `tee` appending to the very file being tailed (that loop feeds
# itself for ever). `--pid` ends the tail when the deploy ends.
if has_tty; then
    tail -n 0 --pid="${DEPLOY_PID}" -f "${LOG}" > /dev/tty 2> /dev/null
fi
wait "${DEPLOY_PID}"
deploy_rc=$?

say ""
say "   log: ${LOG}"
if [[ ${deploy_rc} -ne 0 ]]; then
    if [[ ${NOTHING_NEW} -eq 1 ]]; then
        fail "the detached deploy exited ${deploy_rc} — nothing was released (v${RELEASED} was
       already current), and the stack is not confirmed. Read the log, then re-run
       'make redeploy-web'."
    fi
    fail "the detached deploy exited ${deploy_rc} — v${RELEASED} is released and pushed,
       but the stack is not confirmed. Read the log, then re-run 'make redeploy-web'."
fi
exit 0

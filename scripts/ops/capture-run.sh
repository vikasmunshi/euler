#!/usr/bin/env bash
# Run make targets (or one command) in order, with the whole session captured to audit/logs/.
#
#   bash scripts/ops/capture-run.sh release upgrade-web status-web
#   bash scripts/ops/capture-run.sh redeploy-web
#   bash scripts/ops/capture-run.sh -- sudo journalctl -u euler-auth --since -15min --no-pager
#
# Each argument is a make target, run from the repo root, one after another; the run stops at the
# first failure. After `--` the rest of the line is a single command instead. The session runs under
# script(1), so sudo and release.sh keep a real terminal for their prompts, and everything shown on
# screen lands in the log. Typed input is not recorded (sudo does not echo passwords, so they never
# reach the log).
#
# Log: audit/logs/<timestamp>-<what>.log (0600); audit/logs/latest.log links to the newest. The
# audit/ folder is ignored by git: logs name collaborators and the host's layout.
#
# The run happens inside its own tmux session, as release.sh's does, so the steps outlive this
# terminal: Ctrl-b d detaches, and a dropped connection or a closed web shell costs only the view.
# That matters most for `logout-all` from an `ssh` in the web shell, which closes its own terminal.
# The screen goes when the session ends; the log keeps it. Without tmux, or a terminal to attach
# from, the run stays in this terminal; --no-tmux asks for that.

# shellcheck disable=SC2016  # the echo '…' lines write literal shell text into the session script
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOGS="${ROOT}/audit/logs"

# --log is the outer run naming the file for the one it starts in tmux.
NO_TMUX=0
log=''
while [ $# -gt 0 ]; do
    case "$1" in
        --no-tmux) NO_TMUX=1; shift ;;
        --log) log="${2:?--log needs a file}"; shift 2 ;;
        *) break ;;
    esac
done

if [ $# -eq 0 ]; then
    sed -n '2,21p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
    exit 2
fi
ORIG_ARGS=("$@")

if [ "$1" = '--' ]; then
    shift
    [ $# -gt 0 ] || { echo "error: nothing after --" >&2; exit 2; }
    label="cmd-$(basename "$1")"
    steps=("$(printf '%q ' "$@")")
else
    label="$(IFS=+; echo "$*")"
    steps=()
    for target in "$@"; do
        steps+=("make $(printf '%q' "${target}")")
    done
fi

umask 077
mkdir -p "${LOGS}"
chmod 0700 "${ROOT}/audit" "${LOGS}"
log="${log:-${LOGS}/$(date +%Y%m%d-%H%M%S)-${label//[^A-Za-z0-9+._-]/_}.log}"

# Run the rest inside tmux: its server keeps the pane's terminal open when this one goes, so the
# steps see no hangup and a sudo ticket, which is bound to that terminal, stays good. Each run
# gets its own session, so a second capture can read the logs while a long one waits.
if [ "${NO_TMUX}" -eq 0 ] && [ -z "${TMUX:-}" ] && { : > /dev/tty; } 2> /dev/null; then
    if command -v tmux > /dev/null; then
        # Quoted by hand: tmux hands this to a shell that may not read printf %q's $'…' forms.
        sq() { printf "'%s'" "${1//\'/\'\\\'\'}"; }
        tmux_session="euler-capture-$$"
        rc_file="$(mktemp "${TMPDIR:-/tmp}/euler-capture-rc-XXXXXX")"
        inner="bash $(sq "${ROOT}/scripts/ops/capture-run.sh") --no-tmux --log $(sq "${log}")"
        for arg in "${ORIG_ARGS[@]}"; do inner+=" $(sq "${arg}")"; done
        # tmux reports its own status, never the command's. If this outer run has gone, nobody
        # is left to read the file; the log carries the status.
        inner+="; rc=\$?; if kill -0 $$ 2> /dev/null; then printf '%s' \"\$rc\" > $(sq "${rc_file}")"
        inner+="; else rm -f $(sq "${rc_file}"); fi"

        echo "Running inside tmux session '${tmux_session}' (Ctrl-b d to detach)."
        # A tmux server already running would otherwise hand the pane its own, older PATH.
        tmux new-session -s "${tmux_session}" -c "${ROOT}" -e "PATH=${PATH}" "${inner}"
        rc="$(cat "${rc_file}" 2> /dev/null)"
        if [ -n "${rc}" ]; then
            rm -f "${rc_file}"
            echo "log: ${log} (rc=${rc})"
            exit "${rc}"
        fi
        if tmux has-session -t "${tmux_session}" 2> /dev/null; then
            echo "Detached: still running in '${tmux_session}'."
            echo "  tmux attach -t ${tmux_session}     tail -f ${log}"
            exit 0
        fi
        rm -f "${rc_file}"
        echo "error: the tmux session ended without reporting a status; read ${log}" >&2
        exit 1
    fi
    echo "note: tmux is not installed, so this run ends with this terminal." >&2
fi

# The session script: a header (what, where, which commit), each step with its status, and a
# footer. It stops at the first failing step, and its exit status is that step's.
session="$(mktemp)"
trap 'rm -f "${session}"' EXIT
{
    echo 'set -uo pipefail'
    # The steps run with the ordinary umask, not this wrapper's 077: a venv rebuild run as
    # root would otherwise leave every package unreadable to the service users.
    echo 'umask 022'
    echo "cd $(printf '%q' "${ROOT}")"
    echo 'echo "═══ scripts/ops/capture-run.sh — $(date -Is)"'
    echo 'echo "    user:   $(id -un)   host: $(hostname)"'
    echo 'echo "    repo:   $(git describe --tags --always --dirty) on $(git branch --show-current)  ($(git rev-parse --short HEAD))"'
    echo 'echo "    status: $(git status --short | wc -l) changed path(s)"'
    for step in "${steps[@]}"; do
        echo "echo; echo \"═══ \$(date +%T) \$ $(printf '%s' "${step}" | sed 's/["\\$`]/\\&/g')\""
        echo "${step}"
        echo 'rc=$?'
        echo "echo \"═══ \$(date +%T) rc=\${rc}\""
        echo '[ "${rc}" -eq 0 ] || { echo "═══ stopped: step failed"; exit "${rc}"; }'
    done
    echo 'echo; echo "═══ all steps succeeded — $(git describe --tags --always --dirty)"'
} > "${session}"

script -q -e -c "bash ${session}" "${log}"
rc=$?

chmod 0600 "${log}"
ln -sfn "$(basename "${log}")" "${LOGS}/latest.log"
echo
echo "log: ${log} (rc=${rc})"
exit "${rc}"

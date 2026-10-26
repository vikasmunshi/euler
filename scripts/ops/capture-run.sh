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

# shellcheck disable=SC2016  # the echo '…' lines write literal shell text into the session script
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOGS="${ROOT}/audit/logs"

if [ $# -eq 0 ]; then
    sed -n '2,15p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
    exit 2
fi

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
log="${LOGS}/$(date +%Y%m%d-%H%M%S)-${label//[^A-Za-z0-9+._-]/_}.log"

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

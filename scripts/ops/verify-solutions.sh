#!/usr/bin/env bash
# Re-check every solved problem against its test cases, with a live progress line.
#
#   bash scripts/ops/verify-solutions.sh [LIST | N...]
#   make verify-solutions [LIST=...]
#
#   LIST   the solver list to check (default: {solved}); any list of problems the
#          shell's `loop` takes, e.g. '{solved}[0:10]' for a quick trial run.
#   N...   problem numbers instead, as separate arguments or one argument separated by
#          spaces or commas: `14 76 478`, '14,76,478' (so `make … LIST='14 76'` works too).
#
# The checks run in ONE solver process, fed a command block on stdin (a heredoc): a loop
# over LIST that runs `eval` on each problem and echoes a marker line around it —
# `@@ start N`, then `@@ pass N` or `@@ fail N` by eval's exit status — plus `@@ total T`
# up front. The full output is tee'd to .verify-solutions.log at the repo root (a dot
# file, so gitignored) and piped to the reporter below, which reads only the marker lines.
#
# The log: every run starts it afresh (tee truncates it; nothing is carried over from the
# last run), opens it with a `## start` block (time, command line, list, user, host, pid,
# commit) and closes it with a `## end` block (time, elapsed, exit status, the reporter's
# summary), written on any exit, Ctrl-C included.
#
# One run at a time: the run holds an flock on .verify-solutions.lock for its whole length,
# and a second run refuses to start, before touching the log, rather than truncating the
# log under the first.
#
# eval's own verdict lines stay in the log: `overflow` there is a naive solution refusing
# an input above its safe size, not a failure — eval passes a problem when no solution
# errs or answers wrongly.
#
# The log holds the answers to private problems: it stays in the working tree.
#
# Exits 0 when every problem passes, 1 when any fails or another run holds the lock, 130
# when interrupted, and solver's own status if the shell itself fails.

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOG="$ROOT/.verify-solutions.log"
LOCK="$ROOT/.verify-solutions.lock"
# A list of Problem objects is looped by {loop.number}; a list of bare numbers by {loop}.
if [[ "$*" =~ ^[0-9][0-9,[:space:]]*$ ]]; then
    read -ra numbers <<<"${*//,/ }"
    LIST="[$(IFS=,; echo "${numbers[*]}")]"
    LIST="${LIST//,/, }"
    ITEM='{loop}'
else
    LIST="${1:-{solved\}}"
    ITEM='{loop.number}'
fi
COMMAND="$0${1+ ${*@Q}}"

# The live line redraws in place on a terminal, and prints one line per problem otherwise.
if [[ -t 1 ]]; then CR=$'\r\033[K'; NL=''; else CR=''; NL=$'\n'; fi

clock() { printf '%d:%02d' "$((SECONDS / 60))" "$((SECONDS % 60))"; }
now() { date '+%Y-%m-%d %H:%M:%S %z'; }

# Read solver's output and report progress from the marker lines; ignore everything else.
# The closing summary also goes to $SUMMARY, for the log's end block.
report() {
    local total='?' done=0 passed=0 line n
    local -a failed=()
    while IFS= read -r line; do
        case "$line" in
            '@@ total '*)
                total="${line#@@ total }" ;;
            '@@ start '*)
                n="${line#@@ start }"
                printf '%s[%d/%s] problem %-5s  ✓ %d  ✗ %d  %s%s' "$CR" "$((done + 1))" "$total" "$n" \
                    "$passed" "${#failed[@]}" "$(clock)" "$NL" ;;
            '@@ pass '*)
                done=$((done + 1)); passed=$((passed + 1)) ;;
            '@@ fail '*)
                n="${line#@@ fail }"
                done=$((done + 1)); failed+=("$n")
                printf '%s✗ problem %s failed\n' "$CR" "$n" ;;
        esac
    done
    printf '%s' "$CR"
    {
        printf '%d of %s checked in %s: %d passed, %d failed\n' "$done" "$total" "$(clock)" \
            "$passed" "${#failed[@]}"
        if ((${#failed[@]})); then
            printf 'failed: %s\n' "${failed[*]}"
        fi
    } | tee "$SUMMARY"
    if ((${#failed[@]})); then
        printf 'details: %s\n' "${LOG#"$ROOT"/}"
        return 1
    fi
    [[ "$total" == "$done" ]]   # fewer checked than expected: solver stopped early
}

# The log's end block, on every exit once the lock is held.
# shellcheck disable=SC2317,SC2329  # invoked by the EXIT trap (SC2317 before ShellCheck 0.11)
on_exit() {
    local rc=$?
    {
        printf '## end    %s  (elapsed %s, exit %d%s)\n' "$(now)" "$(clock)" "$rc" \
            "${interrupted:+, interrupted}"
        [[ -s "$SUMMARY" ]] && sed 's/^/##   /' "$SUMMARY"
    } >>"$LOG"
    rm -f "$SUMMARY"
}

cd "$ROOT" || exit 1

# One run at a time. Opened for append, so a refused run leaves the holder's pid intact.
exec 9>>"$LOCK"
if ! flock -n 9; then
    echo "verify-solutions: another run is in progress (pid $(<"$LOCK")); not starting" >&2
    exit 1
fi
echo $$ >"$LOCK"

SUMMARY="$(mktemp)"
interrupted=''
trap on_exit EXIT
trap 'interrupted=1; exit 130' INT TERM

SECONDS=0
# fd 9 (the lock) is closed for everything below: nothing solver starts may outlive the
# run and keep holding it.
{
    printf '## start  %s\n' "$(now)"
    printf '##   command: %s\n' "$COMMAND"
    printf '##   list:    %s\n' "$LIST"
    printf '##   by:      %s@%s, pid %d, in %s\n' "$USER" "$(hostname)" "$$" "$ROOT"
    printf '##   commit:  %s\n' "$(git describe --tags --always --dirty 2>/dev/null || echo unknown)"
    solver <<EOF
total = len($LIST)
echo "@@ total {total}"
loop $LIST: {
    echo "@@ start $ITEM"
    eval $ITEM && echo "@@ pass $ITEM" || echo "@@ fail $ITEM"
}
EOF
} 9>&- | tee "$LOG" 9>&- | report 9>&-
status=("${PIPESTATUS[@]}")
((status[0])) && { echo "solver exited ${status[0]}; see ${LOG#"$ROOT"/}" >&2; exit "${status[0]}"; }
exit "${status[2]}"

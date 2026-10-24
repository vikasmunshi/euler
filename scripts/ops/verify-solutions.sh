#!/usr/bin/env bash
# Re-check every solved problem against its test cases, with a live progress line.
#
#   bash scripts/ops/verify-solutions.sh [LIST]
#
#   LIST   the solver list to check (default: {solved}); any list expression the
#          shell's `loop` takes, e.g. '{solved}[0:10]' for a quick trial run.
#
# The checks run in ONE solver process, fed a command block on stdin (a heredoc): a loop
# over LIST that runs `eval` on each problem and echoes a marker line around it —
# `@@ start N`, then `@@ pass N` or `@@ fail N` by eval's exit status — plus `@@ total T`
# up front. The full output is tee'd to .verify-solutions.log at the repo root (a dot
# file, so gitignored) and piped to the reporter below, which reads only the marker lines.
#
# eval's own verdict lines stay in the log: `overflow` there is a naive solution refusing
# an input above its safe size, not a failure — eval passes a problem when no solution
# errs or answers wrongly.
#
# The log holds the answers to private problems: it stays in the working tree.
#
# Exits 0 when every problem passes, 1 when any fails, and solver's own status if the
# shell itself fails.

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOG="$ROOT/.verify-solutions.log"
LIST="${1:-{solved\}}"

# The live line redraws in place on a terminal, and prints one line per problem otherwise.
if [[ -t 1 ]]; then CR=$'\r\033[K'; NL=''; else CR=''; NL=$'\n'; fi

# Read solver's output and report progress from the marker lines; ignore everything else.
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
    printf '%s%d of %s checked in %s: %d passed, %d failed\n' "$CR" "$done" "$total" "$(clock)" \
        "$passed" "${#failed[@]}"
    if ((${#failed[@]})); then
        printf 'failed: %s\n' "${failed[*]}"
        printf 'details: %s\n' "${LOG#"$ROOT"/}"
        return 1
    fi
    [[ "$total" == "$done" ]]   # fewer checked than expected: solver stopped early
}

clock() { printf '%d:%02d' "$((SECONDS / 60))" "$((SECONDS % 60))"; }

cd "$ROOT" || exit 1
SECONDS=0
solver <<EOF | tee "$LOG" | report
total = len($LIST)
echo "@@ total {total}"
loop $LIST: {
    echo "@@ start {loop.number}"
    eval {loop.number} && echo "@@ pass {loop.number}" || echo "@@ fail {loop.number}"
}
EOF
status=("${PIPESTATUS[@]}")
((status[0])) && { echo "solver exited ${status[0]}; see ${LOG#"$ROOT"/}" >&2; exit "${status[0]}"; }
exit "${status[2]}"

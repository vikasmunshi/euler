#!/usr/bin/env bash
# scripts/c/build.sh — compile a C solution into an executable.
#
# Usage:
#   scripts/c/build.sh <solution.c>
#
# The executable is written next to the solution file, named after the
# solution without the .c extension plus a '_c' suffix (e.g. p0001_s0_c).
# It is made executable so that evaluate.py can discover and run it directly.
# Each solution file is expected to define its own main().
#
# Example:
#   scripts/c/build.sh .euler/p0001_s0.c
#   # produces: .euler/p0001_s0_c  (executable)

set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <solution.c>" >&2
    exit 1
fi

SOLUTION="$1"

if [[ ! -f "${SOLUTION}" ]]; then
    echo "Error: file not found: ${SOLUTION}" >&2
    exit 1
fi

SOLUTION_DIR="$(dirname "${SOLUTION}")"
SOLUTION_BASE="$(basename "${SOLUTION}" .c)"
OUTPUT="${SOLUTION_DIR}/${SOLUTION_BASE}_c"

# Check if output exists and is newer than source
if [[ -f "${OUTPUT}" ]] && [[ "${OUTPUT}" -nt "${SOLUTION}" ]]; then
    echo "Skipping build: ${OUTPUT} is up to date"
    exit 0
fi

set +e
gcc -O2 -Werror -o "${OUTPUT}" "${SOLUTION}" -lm
GCC_EXIT_CODE=$?
set -e

if [[ ${GCC_EXIT_CODE} -eq 0 ]]; then
    chmod +x "${OUTPUT}"
    echo "Built: ${SOLUTION} -> ${OUTPUT}"
else
    echo "Error: build failure  ${SOLUTION}"
    rm -f "${OUTPUT}"
fi

exit ${GCC_EXIT_CODE}

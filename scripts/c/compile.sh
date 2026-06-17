#!/usr/bin/env bash
# scripts/c/build.sh — compile a C solution into an executable.
#
# Usage:
#   scripts/c/compile.sh <solution.c> [--clean]
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
    echo "Usage: $0 <solution.c> [--clean]" >&2
    exit 1
fi

SOLUTION="$1"
CLEAN_FLAG="${2:-}"

if [[ ! -f "${SOLUTION}" ]]; then
    echo "Error: file not found: ${SOLUTION}" >&2
    exit 1
fi

SOLUTION_DIR="$(dirname "${SOLUTION}")"
SOLUTION_BASE="$(basename "${SOLUTION}" .c)"
OUTPUT="${SOLUTION_DIR}/${SOLUTION_BASE}_c"

# Check if output exists and is newer than source
if [[ -f "${OUTPUT}" ]] && [[ "${OUTPUT}" -nt "${SOLUTION}" ]]; then
    if [[ "${CLEAN_FLAG}" != "--clean" ]]; then
        echo "Skipping compile: ${OUTPUT} is up to date"
        exit 0
    fi
fi

# Make the runner framework header (solver/runners/runner.h) discoverable,
# resolved relative to this script so it works regardless of the caller's cwd.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNNER_INCLUDE="${SCRIPT_DIR}/../../solver/runners"

EXTRA_LIBS=""
if grep -q '^#include[[:space:]]*<primesieve\.h>' "${SOLUTION}"; then
    EXTRA_LIBS="${EXTRA_LIBS} -lprimesieve"
fi
# Arbitrary-precision arithmetic: link the bignum library matching each include.
# MPFR depends on GMP, so it pulls in -lgmp too (and must precede it on the line).
if grep -q '^#include[[:space:]]*<mpfr\.h>' "${SOLUTION}"; then
    EXTRA_LIBS="${EXTRA_LIBS} -lmpfr -lgmp"
elif grep -q '^#include[[:space:]]*<gmp\.h>' "${SOLUTION}"; then
    EXTRA_LIBS="${EXTRA_LIBS} -lgmp"
fi
if grep -q '^#include[[:space:]]*<openssl/bn\.h>' "${SOLUTION}"; then
    EXTRA_LIBS="${EXTRA_LIBS} -lcrypto"
fi

set +e
gcc -O2 -Werror -I"${RUNNER_INCLUDE}" -o "${OUTPUT}" "${SOLUTION}" -lm ${EXTRA_LIBS}
GCC_EXIT_CODE=$?
set -e

if [[ ${GCC_EXIT_CODE} -eq 0 ]]; then
    chmod +x "${OUTPUT}"
    echo "Compiled: ${SOLUTION} -> ${OUTPUT}"
else
    echo "Error: compile failed  ${SOLUTION}"
    rm -f "${OUTPUT}"
fi

exit ${GCC_EXIT_CODE}

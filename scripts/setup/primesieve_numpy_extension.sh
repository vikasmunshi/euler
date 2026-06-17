#!/usr/bin/env bash
# primesieve NumPy Extension Setup Script
# =======================================
#
# Builds and installs the optional `primesieve.numpy` extension into the
# project's virtual environment.
#
# Why this script exists:
# The PyPI `primesieve` sdist ships a *pre-generated* `_numpy.cpp` that was
# Cythonized against the legacy NumPy 1.x C-API, and its `setup.py` only re-runs
# Cython when a `.pyx` source is present (which the sdist omits). Under NumPy 2.x
# that stale C++ fails to compile (`PyArray_Descr->subarray`, `NPY_OWNDATA` were
# removed), so a plain `pip install primesieve` builds only the base extension
# and silently skips the NumPy one — leaving `primesieve.numpy.primes()` broken.
#
# This script fetches the real `.pyx`/`.pxd` sources from upstream, re-Cythonizes
# them against the venv's current Cython + NumPy, patches the one remaining
# NumPy-1-ism (`NPY_OWNDATA` -> `NPY_ARRAY_OWNDATA`), then builds and installs a
# wheel with build isolation disabled so the venv's NumPy headers are used.
#
# Prerequisites (apt, via ./scripts/setup/dev_env.sh install primesieve c):
#   - libprimesieve-dev  (primesieve.h + libprimesieve to link against)
#   - a C/C++ toolchain  (build-essential, gcc)
# Python build deps (cython, numpy, setuptools) are ensured in the venv below.
#
# Author: Vikas Munshi <vikas.munshi@gmail.com>
# Copyright (c) 2024. All rights reserved.
# Licensed under the MIT License.

set -euo pipefail

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

# Project root is two levels up from this script (scripts/setup/<this>).
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# The venv to install into; overridable via the VENV environment variable.
VENV="${VENV:-${PROJECT_ROOT}/.venv}"
PYTHON="${VENV}/bin/python"
PIP="${PYTHON} -m pip"

# Upstream repository providing the Cython sources omitted from the sdist.
UPSTREAM_RAW="https://raw.githubusercontent.com/shlomif/primesieve-python"
# Git ref to fetch the .pyx/.pxd sources from; override via PRIMESIEVE_REF.
PRIMESIEVE_REF="${PRIMESIEVE_REF:-master}"

usage() {
    echo "Usage: $0 [install|check|uninstall]"
    echo
    echo "  install    Build and install the primesieve.numpy extension (default)"
    echo "  check      Verify the primesieve.numpy extension imports and works"
    echo "  uninstall  Remove the primesieve package from the venv"
}

# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

# Aborts with a message if the project venv is missing.
require_venv() {
    if [[ ! -x "${PYTHON}" ]]; then
        echo "Error: venv python not found at ${PYTHON}" >&2
        echo "Create the venv first (e.g. 'make install-minimal' or 'python3.14 -m venv .venv')." >&2
        exit 1
    fi
}

# Returns 0 if the compiled primesieve.numpy extension imports and produces the
# expected primes for a known range, 1 otherwise.
numpy_ext_works() {
    "${PYTHON}" - <<'PY' >/dev/null 2>&1
import primesieve.numpy as psnp
assert psnp.primes(20).tolist() == [2, 3, 5, 7, 11, 13, 17, 19]
PY
}

# Ensures the Python build dependencies are present in the venv.
ensure_build_deps() {
    if ! "${PYTHON}" -c "import cython, numpy, setuptools" >/dev/null 2>&1; then
        echo "Installing build dependencies (cython, numpy, setuptools)..."
        ${PIP} install --upgrade cython numpy setuptools
    fi
}

# --------------------------------------------------------------------------
# Actions
# --------------------------------------------------------------------------

# Builds the NumPy-enabled primesieve wheel from a patched sdist and installs it.
install_extension() {
    require_venv

    if numpy_ext_works; then
        echo "primesieve.numpy extension already installed and working — nothing to do."
        return 0
    fi

    ensure_build_deps

    local workdir src ext_dir
    workdir="$(mktemp -d)"
    # shellcheck disable=SC2064
    trap "rm -rf '${workdir}'" RETURN

    echo "Downloading primesieve sdist..."
    ${PIP} download --no-binary :all: --no-deps --no-build-isolation \
        primesieve -d "${workdir}"

    echo "Extracting sdist..."
    tar -C "${workdir}" -xzf "${workdir}"/primesieve-*.tar.gz
    src="$(find "${workdir}" -maxdepth 1 -type d -name 'primesieve-*' | head -n1)"
    if [[ -z "${src}" ]]; then
        echo "Error: could not locate extracted primesieve source directory" >&2
        return 1
    fi
    ext_dir="${src}/primesieve"

    echo "Fetching Cython sources from ${PRIMESIEVE_REF}..."
    curl -fsSL "${UPSTREAM_RAW}/${PRIMESIEVE_REF}/primesieve/_primesieve.pyx" \
        -o "${ext_dir}/_primesieve.pyx"
    curl -fsSL "${UPSTREAM_RAW}/${PRIMESIEVE_REF}/primesieve/cpp_primesieve.pxd" \
        -o "${ext_dir}/cpp_primesieve.pxd"
    curl -fsSL "${UPSTREAM_RAW}/${PRIMESIEVE_REF}/primesieve/numpy/_numpy.pyx" \
        -o "${ext_dir}/numpy/_numpy.pyx"
    curl -fsSL "${UPSTREAM_RAW}/${PRIMESIEVE_REF}/primesieve/numpy/cpp_numpy.pxd" \
        -o "${ext_dir}/numpy/cpp_numpy.pxd"

    # Patch the one NumPy-1-ism: the C-API flag alias was renamed in NumPy 2.x.
    # No-op if upstream has already fixed it.
    sed -i 's/np\.NPY_OWNDATA/np.NPY_ARRAY_OWNDATA/' "${ext_dir}/numpy/_numpy.pyx"

    # Drop the stale generated C++ so the presence of the .pyx switches setup.py
    # to its Cython path and regenerates against the venv's NumPy.
    rm -f "${ext_dir}/_primesieve.cpp" "${ext_dir}/numpy/_numpy.cpp"

    echo "Building wheel (no build isolation, using the venv's Cython + NumPy)..."
    ${PIP} wheel "${src}" --no-build-isolation --no-deps -w "${workdir}/wheel"

    echo "Installing wheel..."
    ${PIP} install --force-reinstall --no-deps --no-cache-dir \
        "${workdir}"/wheel/primesieve-*.whl

    if numpy_ext_works; then
        echo "✓ primesieve.numpy extension installed and verified."
    else
        echo "Error: build completed but the primesieve.numpy extension still fails." >&2
        return 1
    fi
}

# Verifies the extension; exits nonzero if it is missing or broken.
check_extension() {
    require_venv
    if numpy_ext_works; then
        echo "✓ primesieve.numpy extension is installed and working."
    else
        echo "✗ primesieve.numpy extension is missing or broken. Run: $0 install" >&2
        return 1
    fi
}

# Removes the primesieve package from the venv.
uninstall_extension() {
    require_venv
    ${PIP} uninstall -y primesieve
    echo "✓ primesieve removed from the venv."
}

# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

main() {
    local action="${1:-install}"
    case "${action}" in
        install)   install_extension ;;
        check)     check_extension ;;
        uninstall) uninstall_extension ;;
        -h|--help|help) usage ;;
        *) echo "Error: unknown action '${action}'" >&2; usage; exit 1 ;;
    esac
}

main "$@"

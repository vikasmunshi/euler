#!/usr/bin/env bash
# Shared system-venv helpers (DD-5) — the root-owned /opt/euler venv every euler-*
# app service runs from
# ==========================================================================================
#
# Sourced by the app-service kits (auth.sh / user.sh) so the venv location, the
# installed dependency set, and the deploy/clean logic have **one** definition
# instead of drifting copies. Can also be run directly for a manual
# `venv.sh deploy|clean|status`.
#
# The venv is deliberately **not** the operator's `.venv`: the services run as locked-down
# euler-* uids that cannot read the operator's home (DD-5), so the code lives in a
# root-owned tree at /opt/euler, group-readable by euler-web, and the units run
# `/opt/euler/venv/bin/python -m solver.web.<svc>`.
#
# Author: Vikas Munshi <vikas.munshi@gmail.com>
# Copyright (c) 2026. All rights reserved.
# Licensed under the MIT License.

# The system venv (DD-5): root-owned, at /opt/euler; the services run its python.
OPT_DIR="/opt/euler"
VENV_DIR="${OPT_DIR}/venv"
VENV_PY="${VENV_DIR}/bin/python"
PYTHON="${PYTHON:-python3.14}"          # the project floor; deadsnakes on 24.04

# Dependency groups installed into the system venv. Beyond `web` (the app services
# themselves), a web shell is the full solver: `ai` so a maintainer's `claude-*`
# work once the Phase-7 broker supplies the key (the anthropic SDK must be present);
# `solutions` so `eval`/`benchmark` can build the sieves/tables real solutions need;
# `dev` because `new`/`lint` shell out to black/isort/autoflake/flake8. `show`
# (matplotlib/PyQt5) is **excluded** — GUI plotting has no place on a headless server.
VENV_EXTRAS="ai,dev,solutions,web"

# Build/refresh the root-owned system venv and (re)install the repo into it so the
# DEPLOYED package always matches the current source (the units run `-m solver.web.*`
# with cwd=/, so a stale venv fails even when the repo has the module). Idempotent —
# every kit calls it, and installing again is a cheap refresh.
#   $1 = the repo root to install from   $2 = the group that owns the venv (euler-web)
deploy_venv() {
    local project_root="$1" web_group="$2"
    if [ ! -x "${VENV_PY}" ]; then
        echo "Creating system venv at ${VENV_DIR} (${PYTHON})..."
        sudo mkdir -p "${OPT_DIR}"
        sudo "${PYTHON}" -m venv "${VENV_DIR}"
    fi
    echo "Installing solver[${VENV_EXTRAS}] into ${VENV_DIR} (as root, from ${project_root})..."
    sudo "${VENV_PY}" -m pip install --quiet --upgrade pip
    sudo "${VENV_PY}" -m pip install --quiet "${project_root}[${VENV_EXTRAS}]"
    # The `solutions` extra installs the base `primesieve` wheel, which SKIPS the
    # numpy extension (its sdist ships NumPy-1.x-era C++ that won't build under 2.x).
    # `pip install` alone therefore leaves `primesieve.numpy` importable-but-broken in
    # the system venv — every numpy-backed solution fails at runtime in the web tier.
    # Build it from source here so a deployed venv matches a developer's (idempotent:
    # the script no-ops when the extension already imports). Best-effort — a build
    # failure (missing libprimesieve-dev / toolchain) must not abort the whole deploy.
    echo "Building the primesieve.numpy extension into ${VENV_DIR}..."
    if ! sudo VENV="${VENV_DIR}" bash "${project_root}/scripts/setup/primesieve_numpy_extension.sh" install; then
        echo "warn: primesieve.numpy build failed — numpy-backed solutions will break at runtime."
        echo "      Fix the toolchain (dev_env.sh install primesieve c) then re-run 'venv.sh deploy'."
    fi
    sudo chown -R root:"${web_group}" "${OPT_DIR}"
    clean_build_artifacts "${project_root}"
}

# Remove the in-tree build artifacts the setuptools backend leaves behind. A source
# install (`pip install <path>[...]`, not a wheel) builds *in place*, dropping `build/`
# and `solver.egg-info/` into the repo — gitignored, but they dirty the tree and the
# egg-info lands root-owned (the install ran under sudo). Neither is needed after the
# install: the deployed venv carries its own dist-info, and the operator's local
# editable install resolves via a PEP 660 `.pth` finder pointing at the source, not the
# egg-info. Remove under sudo to cover the root-owned egg-info; never fail the deploy on it.
clean_build_artifacts() {
    local project_root="$1"
    sudo rm -rf "${project_root}/build" "${project_root}"/*.egg-info 2>/dev/null || true
}

# True when the deployed venv can import *module* (build-order gate). -P ignores cwd, so
# this probes the venv's site-packages, not the repo the caller is standing in.
venv_has_module() {
    [ -x "${VENV_PY}" ] && sudo "${VENV_PY}" -P -c "import $1" 2>/dev/null
}

# ── standalone use (venv.sh deploy|clean|status) ──────────────────────────────────
# Only when executed directly, not when sourced. Derives the repo root from this
# script's location (scripts/setup/venv.sh → up 2).
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    set -euo pipefail
    _repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
    case "${1:-status}" in
        deploy) deploy_venv "${_repo}" "euler-web" ;;
        clean)  clean_build_artifacts "${_repo}"; echo "Removed in-tree build/ and *.egg-info." ;;
        status)
            if venv_has_module solver; then
                echo "venv: ✓ solver importable from ${VENV_DIR} ([${VENV_EXTRAS}])"
            else
                echo "venv: ✗ ${VENV_DIR} not deployed (run 'venv.sh deploy' or a kit's install)"
            fi ;;
        -h | --help | help) echo "Usage: $0 [deploy|clean|status]  (deploy needs sudo)" ;;
        *) echo "Unknown action: ${1}"; echo "Usage: $0 [deploy|clean|status]"; exit 1 ;;
    esac
fi

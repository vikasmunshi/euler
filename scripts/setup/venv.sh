#!/usr/bin/env bash
# Shared system-venv helpers — the root-owned /opt/euler venv every euler-*
# app service runs from
# ==========================================================================================
#
# Sourced by the app-service kits (auth.sh / user.sh) so the venv location, the
# installed dependency set, and the deploy/clean logic have **one** definition
# instead of drifting copies. Can also be run directly for a manual
# `venv.sh deploy|remove|redeploy|clean|status`.
#
# The venv is deliberately **not** the operator's `.venv`: the services run as locked-down
# euler-* uids that cannot read the operator's home, so the code lives in a
# root-owned tree at /opt/euler, group-readable by euler-web, and the units run
# `/opt/euler/venv/bin/python -m solver.web.<svc>`.
#
# Author: Vikas Munshi <vikas.munshi@gmail.com>
# Copyright (c) 2026. All rights reserved.
# Licensed under the MIT License.

# The system venv: root-owned, at /opt/euler; the services run its python.
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
    # setuptools-scm derives the version from `git describe` at build time, but the
    # build runs as ROOT against the operator-OWNED checkout: root's git does not
    # resolve the checkout's tags the way the owner's does (no safe.directory for the
    # foreign repo), so the wheel froze a tag-less `0.0.1.devN+g<sha>` instead of the
    # release number. Compute the version HERE as the checkout owner — who resolves
    # the tag correctly — and hand it to the root build via setuptools-scm's PRETEND
    # override. Only when HEAD is exactly on a `vX.Y.Z` tag (a release); off-tag dev
    # deploys leave it unset and take setuptools-scm's normal dev string.
    # `--long --dirty` always prints `v<X.Y.Z>-<distance>-g<sha>[-dirty]` (or fails,
    # `|| :`, when there is no tag yet — leaving scm_version empty so the build takes
    # setuptools-scm's own dev string). Exactly on a clean tag → the release number
    # `X.Y.Z`; otherwise a PEP 440 local version `X.Y.Z+<distance>.g<sha>[.dirty]` that
    # is clean, correct, and clearly post-release. Computed here as the checkout owner
    # because the root build's git does not resolve the owner's tag.
    local scm_version="" desc
    desc="$(git -C "${project_root}" describe --tags --long --dirty --match 'v*' 2>/dev/null)" || :
    if [[ "${desc}" =~ ^v([0-9]+\.[0-9]+\.[0-9]+)-([0-9]+)-g([0-9a-f]+)(-dirty)?$ ]]; then
        local base="${BASH_REMATCH[1]}" dist="${BASH_REMATCH[2]}" sha="${BASH_REMATCH[3]}"
        local dirty="${BASH_REMATCH[4]:+.dirty}"
        if [[ "${dist}" == 0 && -z "${dirty}" ]]; then
            scm_version="${base}"
        else
            scm_version="${base}+${dist}.g${sha}${dirty}"
        fi
    fi
    sudo env ${scm_version:+SETUPTOOLS_SCM_PRETEND_VERSION_FOR_SOLVER="${scm_version}"} \
        "${VENV_PY}" -m pip install --quiet "${project_root}[${VENV_EXTRAS}]"
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

# Tear the root-owned system venv back out — remove the whole /opt/euler tree (the venv
# plus the primesieve.numpy build products under it). The app-service kits (auth.sh /
# user.sh) manage their own identities, state, and units; this only drops the shared
# venv, so run it when no euler-* service still needs it. Idempotent — a no-op when
# /opt/euler is already gone.
remove_venv() {
    if [ -d "${OPT_DIR}" ]; then
        echo "Removing the system venv at ${OPT_DIR}..."
        sudo rm -rf "${OPT_DIR}"
    else
        echo "No system venv at ${OPT_DIR} — nothing to remove."
    fi
}

# ── standalone use (venv.sh deploy|clean|status) ──────────────────────────────────
# Only when executed directly, not when sourced. Derives the repo root from this
# script's location (scripts/setup/venv.sh → up 2).
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    set -euo pipefail
    _repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
    case "${1:-status}" in
        deploy) deploy_venv "${_repo}" "euler-web" ;;
        remove) remove_venv ;;
        redeploy) remove_venv; deploy_venv "${_repo}" "euler-web" ;;
        clean)  clean_build_artifacts "${_repo}"; echo "Removed in-tree build/ and *.egg-info." ;;
        status)
            if venv_has_module solver; then
                echo "venv: ✓ solver importable from ${VENV_DIR} ([${VENV_EXTRAS}])"
            else
                echo "venv: ✗ ${VENV_DIR} not deployed (run 'venv.sh deploy' or a kit's deploy)"
            fi ;;
        -h | --help | help) echo "Usage: $0 [deploy|remove|redeploy|clean|status]  (deploy/remove/redeploy need sudo)" ;;
        *) echo "Unknown action: ${1}"; echo "Usage: $0 [deploy|remove|redeploy|clean|status]"; exit 1 ;;
    esac
fi

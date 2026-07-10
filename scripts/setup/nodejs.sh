#!/usr/bin/env bash
# Standalone Node.js (dev tooling) — no sudo, no apt
# ==================================================
#
# Installs / uninstalls a pinned standalone Node.js under ~/.local, used only by
# developer tooling — currently the JS↔Python SRP interop test
# (tests/test_srp_interop.py, driving solver/web/content/assets/srp.js against
# solver/web/auth/srp.py). It is NOT a runtime dependency: no service, no unit,
# nothing system-wide — which is why this kit, unlike its scripts/setup siblings,
# needs no sudo and installs no systemd unit.
#
#   ~/.local/opt/node-v<version>-linux-x64/   the unpacked official tarball
#   ~/.local/bin/node                         symlink to its node binary
#
# Actions: install | uninstall | status | help
#
# Author: Vikas Munshi <vikas.munshi@gmail.com>
# Copyright (c) 2026. All rights reserved.
# Licensed under the MIT License.

set -euo pipefail

NODE_VERSION="${EULER_NODE_VERSION:-22.14.0}"
NODE_DIST="node-v${NODE_VERSION}-linux-x64"
OPT_DIR="${HOME}/.local/opt"
NODE_DIR="${OPT_DIR}/${NODE_DIST}"
BIN_DIR="${HOME}/.local/bin"
NODE_LINK="${BIN_DIR}/node"
TARBALL_URL="https://nodejs.org/dist/v${NODE_VERSION}/${NODE_DIST}.tar.xz"

usage() {
    cat <<USAGE
Usage: $0 [install|uninstall|status|help]

  install    Download the official ${NODE_DIST} tarball into ~/.local/opt and
             symlink ~/.local/bin/node (idempotent; no sudo).
  uninstall  Remove the ~/.local/opt tree and the node symlink.
  status     Report the installed version and symlink health.

  Dev-only tooling: drives the SRP interop test (tests/test_srp_interop.py),
  which auto-skips when node is absent. Override the pinned version with
  EULER_NODE_VERSION.
USAGE
}

do_install() {
    if [ -x "${NODE_DIR}/bin/node" ]; then
        echo "node v${NODE_VERSION} already at ${NODE_DIR}"
    else
        echo "Downloading ${TARBALL_URL}..."
        mkdir -p "${OPT_DIR}"
        curl -fsSL "${TARBALL_URL}" | tar -xJ -C "${OPT_DIR}"
    fi
    mkdir -p "${BIN_DIR}"
    ln -sf "${NODE_DIR}/bin/node" "${NODE_LINK}"
    echo "✓ $("${NODE_DIR}/bin/node" --version) installed (${NODE_LINK})"
    if ! command -v node &> /dev/null; then
        echo "note: ${BIN_DIR} is not on your PATH."
    fi
}

do_uninstall() {
    rm -rf "${NODE_DIR}"
    if [ -L "${NODE_LINK}" ]; then
        rm -f "${NODE_LINK}"
    fi
    echo "✓ node v${NODE_VERSION} removed"
}

do_status() {
    if [ -x "${NODE_DIR}/bin/node" ]; then
        echo "node:    ✓ $("${NODE_DIR}/bin/node" --version) at ${NODE_DIR}"
    else
        echo "node:    ✗ not installed (v${NODE_VERSION} pinned)"
    fi
    if [ -L "${NODE_LINK}" ] && [ -x "${NODE_LINK}" ]; then
        echo "symlink: ✓ ${NODE_LINK} -> $(readlink "${NODE_LINK}")"
    else
        echo "symlink: ✗ ${NODE_LINK} absent"
    fi
}

# ── Dispatch ──────────────────────────────────────────────────────────────────────
ACTION="${1:-status}"
case "${ACTION}" in
    install)   do_install ;;
    uninstall) do_uninstall ;;
    status)    do_status ;;
    -h | --help | help) usage ;;
    *) echo "Unknown action: ${ACTION}"; usage; exit 1 ;;
esac

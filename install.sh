#!/usr/bin/env bash
# Project Euler Solver — one-line installer
#
#   curl -fsSL https://raw.githubusercontent.com/vikasmunshi/euler/master/install.sh | bash
#   curl -fsSL https://raw.githubusercontent.com/vikasmunshi/euler/master/install.sh | bash -s -- --dir ~/projects/euler
#
# Options:
#   --dir <path>   Clone destination (default: ~/euler)
#   --help         Show this message
#
# Author: Vikas Munshi <vikas.munshi@gmail.com>
# Licensed under the MIT License.

set -euo pipefail

REPO_URL="https://github.com/vikasmunshi/euler.git"
INSTALL_DIR="${HOME}/euler"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dir)    [[ -n "${2-}" ]] || { echo "error: --dir requires a value" >&2; exit 1; }
                  INSTALL_DIR="$2"; shift 2 ;;
        --dir=*)  INSTALL_DIR="${1#*=}"; shift ;;
        -h|--help)
            echo "Usage: curl -fsSL .../install.sh | bash -s -- [--dir <path>]"
            exit 0 ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

if [[ $EUID -eq 0 ]]; then
    echo "error: do not run as root — sudo will be used when needed" >&2
    exit 1
fi

# Ensure make is available (pulls in build-essential on Debian/Ubuntu)
if ! command -v make &>/dev/null; then
    sudo apt install -y build-essential
fi

# Clone or update
INSTALL_DIR="${INSTALL_DIR%/}"
if [[ -d "${INSTALL_DIR}/.git" ]]; then
    echo "Repository already exists at ${INSTALL_DIR} — pulling latest."
    git -C "$INSTALL_DIR" pull --ff-only
else
    git clone "$REPO_URL" "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"
mkdir workspace || true
make install-all
source .venv/bin/activate

echo ""
echo "Installation complete. To get started:"
echo "  source ${INSTALL_DIR}/.venv/bin/activate"
echo "  solver"
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

# Platform guard — the build installs Python 3.14 from the deadsnakes PPA and
# the Makefile runs `python3.14 -m venv`. That toolchain is only validated on
# Ubuntu 24.04+; on Ubuntu 22.04 (and older) `make install-all` fails deep in
# apt, so bail out early here with a clear message instead.
MIN_UBUNTU_MAJOR=24
if [[ "$(uname -s)" != "Linux" ]]; then
    echo "error: this installer supports Ubuntu Linux only (found $(uname -s))." >&2
    exit 1
fi
if ! command -v apt-get &>/dev/null; then
    echo "error: 'apt-get' not found — this installer requires Ubuntu/Debian." >&2
    exit 1
fi
if [[ -r /etc/os-release ]]; then
    # shellcheck disable=SC1091
    . /etc/os-release
    case "${ID:-}" in
        ubuntu)
            ubuntu_major="${VERSION_ID%%.*}"
            if [[ -z "$ubuntu_major" || ! "$ubuntu_major" =~ ^[0-9]+$ ]]; then
                echo "warning: could not parse Ubuntu version '${VERSION_ID:-?}'; continuing." >&2
            elif (( ubuntu_major < MIN_UBUNTU_MAJOR )); then
                echo "error: Ubuntu ${VERSION_ID:-?} is not supported." >&2
                echo "       This project needs Python 3.14 and is tested on Ubuntu ${MIN_UBUNTU_MAJOR}.04+." >&2
                echo "       Please upgrade to Ubuntu ${MIN_UBUNTU_MAJOR}.04 or newer." >&2
                exit 1
            fi
            ;;
        *)
            echo "warning: '${PRETTY_NAME:-${ID:-unknown}}' is untested." >&2
            echo "         This installer is validated on Ubuntu ${MIN_UBUNTU_MAJOR}.04+ and may fail elsewhere." >&2
            ;;
    esac
else
    echo "warning: /etc/os-release not found; skipping OS version check." >&2
fi

# Ensure git is available (needed to clone the repository below)
if ! command -v git &>/dev/null; then
    sudo apt install -y git
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

# Install a quick-start launcher at ~/.local/bin/euler
LAUNCHER_DIR="${HOME}/.local/bin"
LAUNCHER="${LAUNCHER_DIR}/euler"
INSTALL_DIR="$(realpath "$INSTALL_DIR")"
mkdir -p "$LAUNCHER_DIR"
cat > "$LAUNCHER" <<EOF
#!/usr/bin/env bash
# Quick-start launcher for the Project Euler Solver (installed by ${INSTALL_DIR}/install.sh)
#
# Usage: euler [--web | --shell] [args...]
#   --web    (default) start the browser front end and open it
#   --shell  run the interactive terminal shell
set -euo pipefail

usage() {
    echo "Usage: euler [--web | --shell] [args...]"
    echo "  --web    (default) start the interactive web shell"
    echo "  --shell  start the interactive terminal shell"
    exit 0
}

mode="web"
case "\${1-}" in
    --web)   mode="web";   shift ;;
    --shell) mode="shell"; shift ;;
    -h|--help) usage ;;
esac

cd "${INSTALL_DIR}" || exit 1
source .venv/bin/activate

if [[ "\$mode" == "shell" ]]; then
    # Interactive terminal shell — replaces this process.
    exec .venv/bin/solver "\$@"
elif [[ "\$mode" == "web" ]]; then
    # Web mode: start (or reuse) the server.
    .venv/bin/solver-web "\$@"
else
    usage
fi
EOF
chmod +x "$LAUNCHER"

echo ""
echo "Installation complete. To get started:"
echo "  euler            # web front end (default)"
echo "  euler --shell    # interactive terminal shell"
if ! command -v euler &>/dev/null; then
    echo ""
    echo "note: ${LAUNCHER_DIR} is not on your PATH. Add it with:"
    echo "  export PATH=\"${LAUNCHER_DIR}:\$PATH\""
    echo "Or run the launcher directly: ${LAUNCHER}"
fi
echo ""
echo "Or activate the virtual environment manually:"
echo "  cd ${INSTALL_DIR}"
echo "  source .venv/bin/activate"
echo "  solver"
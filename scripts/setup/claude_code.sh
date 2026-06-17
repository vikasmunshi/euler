#!/usr/bin/env bash
# Claude Code CLI Setup Script
# ============================
#
# Installs, updates, or removes the Claude Code CLI (`claude`) — Anthropic's
# agentic coding tool. This project uses it for the `claude-solver` shell
# command and the in-shell `claude-euler-solver` skill (see solver/ai/skill.py).
#
# Installation uses Anthropic's native installer (https://claude.ai/install.sh),
# which places a self-contained `claude` binary under ~/.local/bin — no Node.js
# and no sudo required. If `curl` is unavailable it falls back to a global npm
# install of @anthropic-ai/claude-code.
#
# Features:
# - Checks for an existing Claude Code installation (idempotent install)
# - Installs the latest stable version via the native installer (npm fallback)
# - Updates an existing install in place
# - Links the project-root `.claude/` and `CLAUDE.md` to the canonical copies
#   under solver/ai/claude/ (idempotent; any pre-existing file is backed up,
#   never deleted)
# - Uninstalls cleanly (binary, local install data, optional user config)
# - Warns if ~/.local/bin is not on PATH
#
# Author: Vikas Munshi <vikas.munshi@gmail.com>
# Copyright (c) 2026. All rights reserved.
# Licensed under the MIT License.

set -euo pipefail

INSTALLER_URL="https://claude.ai/install.sh"
NPM_PACKAGE="@anthropic-ai/claude-code"
LOCAL_BIN="${HOME}/.local/bin"
CLAUDE_BIN="${LOCAL_BIN}/claude"
CLAUDE_DATA_DIR="${HOME}/.local/share/claude"

# Project root, derived from this script's location (scripts/setup/claude_code.sh),
# so the symlink helpers work regardless of the caller's current directory.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

usage() {
    echo "Usage: $0 [install|update|uninstall|status]"
    echo
    echo "  install    Install Claude Code if missing (default if no argument given)"
    echo "  update     Update an existing install to the latest version"
    echo "  uninstall  Remove the Claude Code binary and local install data"
    echo "  status     Show installation state and version"
}

# Returns 0 if the `claude` command is resolvable on PATH, 1 otherwise.
claude_is_installed() {
    command -v claude &> /dev/null
}

# Print the installed version using the freshly installed binary, tolerating a
# PATH that does not yet include ~/.local/bin in the current shell.
claude_version() {
    PATH="${LOCAL_BIN}:${PATH}" claude --version 2>/dev/null || echo "unknown"
}

# Warn (don't fail) if ~/.local/bin — where the native installer drops the
# binary — is not on PATH, so the user knows why `claude` isn't found yet.
print_path_hint() {
    case ":${PATH}:" in
        *":${LOCAL_BIN}:"*) ;;
        *)
            echo "Note: ${LOCAL_BIN} is not on your PATH."
            echo "      Add it, e.g.:  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc"
            ;;
    esac
}

# Installs Claude Code via the native installer, falling back to npm.
install_claude() {
    if claude_is_installed; then
        echo "Claude Code is already installed: $(claude --version 2>/dev/null || echo present)"
        return 0
    fi

    echo "Installing Claude Code..."
    if command -v curl &> /dev/null; then
        curl -fsSL "${INSTALLER_URL}" | bash
    elif command -v npm &> /dev/null; then
        echo "curl not found; falling back to npm..."
        npm install -g "${NPM_PACKAGE}"
    else
        echo "Error: need either curl (preferred) or npm to install Claude Code." >&2
        return 1
    fi

    echo "Claude Code installation completed: $(claude_version)"
    print_path_hint
}

# Updates an existing Claude Code install in place (installs it if missing).
update_claude() {
    if ! claude_is_installed; then
        echo "Claude Code is not installed; installing instead..."
        install_claude
        return 0
    fi

    echo "Updating Claude Code..."
    if claude update 2> /dev/null; then
        : # native self-updater handled it
    elif command -v curl &> /dev/null; then
        curl -fsSL "${INSTALLER_URL}" | bash
    elif command -v npm &> /dev/null; then
        npm install -g "${NPM_PACKAGE}"
    fi
    echo "Claude Code now at: $(claude_version)"
}

# Removes the Claude Code binary, local install data, and (with confirmation)
# the user configuration. Also removes a global npm install if present.
uninstall_claude() {
    if ! claude_is_installed && [ ! -e "${CLAUDE_BIN}" ] && [ ! -d "${CLAUDE_DATA_DIR}" ]; then
        echo "Claude Code does not appear to be installed"
        return 0
    fi

    if command -v npm &> /dev/null && npm ls -g "${NPM_PACKAGE}" &> /dev/null; then
        echo "Removing global npm package ${NPM_PACKAGE}..."
        npm uninstall -g "${NPM_PACKAGE}" || true
    fi

    if [ -e "${CLAUDE_BIN}" ]; then
        echo "Removing ${CLAUDE_BIN}"
        rm -f "${CLAUDE_BIN}"
    fi

    if [ -d "${CLAUDE_DATA_DIR}" ]; then
        echo "Removing ${CLAUDE_DATA_DIR}"
        rm -rf "${CLAUDE_DATA_DIR}"
    fi

    if [ -d "${HOME}/.claude" ]; then
        read -r -p "Remove Claude Code user configuration (~/.claude)? [y/N] " reply
        if [[ "${reply}" =~ ^[Yy]$ ]]; then
            echo "Removing Claude Code user configuration under ~/.claude"
            rm -rf "${HOME}/.claude"
        else
            echo "Keeping Claude Code user configuration"
        fi
    fi

    echo "Claude Code uninstallation completed"
}

# Create one relative symlink ${PROJECT_ROOT}/<name> -> <target>, idempotently.
# If the path is already that symlink, nothing happens. Anything else in the way
# (a real file/dir, or a symlink pointing elsewhere) is moved aside to a
# timestamped backup rather than deleted, then the link is created. A missing
# target is skipped with a warning.
link_one() {
    local name="$1" target="$2"
    local link="${PROJECT_ROOT}/${name}"

    if [ ! -e "${PROJECT_ROOT}/${target}" ]; then
        echo "Warning: link target ${target} is missing; skipping ${name}" >&2
        return 0
    fi

    # Already the symlink we want — nothing to do.
    if [ -L "${link}" ] && [ "$(readlink "${link}")" = "${target}" ]; then
        return 0
    fi

    # Something else is in the way (real file/dir, or a symlink to another target,
    # or a dangling symlink). Preserve it: move it aside, never delete.
    if [ -e "${link}" ] || [ -L "${link}" ]; then
        local backup
        backup="${link}.bak.$(date +%Y%m%d%H%M%S)"
        echo "Backing up existing ${name} -> ${backup##*/}"
        mv "${link}" "${backup}"
    fi

    ln -s "${target}" "${link}"
    echo "Linked ${name} -> ${target}"
}

# Expose the package's Claude Code config at the project root, where the `claude`
# CLI and IDE integrations expect `.claude/` and `CLAUDE.md`. The canonical copies
# are version-controlled under solver/ai/claude/; these are relative symlinks to
# them (recreated here in case a checkout did not preserve them).
link_project_config() {
    link_one ".claude" "solver/ai/claude"
    link_one "CLAUDE.md" "solver/ai/claude/CLAUDE.md"
}

# Reports the state of one project-root symlink for `status`.
status_link() {
    local name="$1" target="$2"
    local link="${PROJECT_ROOT}/${name}"
    if [ -L "${link}" ]; then
        echo "  ${name}: ✓ -> $(readlink "${link}")"
    elif [ -e "${link}" ]; then
        echo "  ${name}: ✗ present but not a symlink"
    else
        echo "  ${name}: ✗ missing (run install to create it)"
    fi
}

# Reports whether Claude Code is installed, where, and its version.
status_claude() {
    if claude_is_installed; then
        echo "Claude Code: ✓ installed ($(command -v claude))"
        echo "  version: $(claude --version 2>/dev/null || echo unknown)"
    else
        echo "Claude Code: ✗ not installed"
        print_path_hint
    fi
    echo "Project config links:"
    status_link ".claude" "solver/ai/claude"
    status_link "CLAUDE.md" "solver/ai/claude/CLAUDE.md"
}

# Main execution — defaults to 'install' if no argument provided.
ACTION="${1:-install}"

case "${ACTION}" in
    install)
        install_claude
        link_project_config
        ;;
    update)
        update_claude
        link_project_config
        ;;
    uninstall)
        uninstall_claude
        ;;
    status)
        status_claude
        ;;
    -h | --help | help)
        usage
        ;;
    *)
        echo "Unknown action: ${ACTION}"
        usage
        exit 1
        ;;
esac
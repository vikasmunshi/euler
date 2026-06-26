#!/usr/bin/env bash
# Git Hooks Setup Script
# ======================
#
# Installs/uninstalls the project's git hooks by rendering templates from
# scripts/setup/hooks/ into .git/hooks/.
#
# Hooks managed:
#   - pre-commit  (.git/hooks/pre-commit)
#   - pre-push    (.git/hooks/pre-push)
#
# Author: Vikas Munshi <vikas.munshi@gmail.com>
# Copyright (c) 2024. All rights reserved.
# Licensed under the MIT License.

set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)"
HOOKS_DIR="${REPO_ROOT}/.git/hooks"
TEMPLATES_DIR="${REPO_ROOT}/scripts/setup/hooks"

PRE_COMMIT="${HOOKS_DIR}/pre-commit"
PRE_PUSH="${HOOKS_DIR}/pre-push"

VENV="${REPO_ROOT}/.venv"

FORCE=0

usage() {
    cat <<EOF
Usage: $0 [install|uninstall] [--force]

  install      Write git hooks into .git/hooks/ (default)
  uninstall    Remove the managed hooks from .git/hooks/
  --force      Overwrite existing hooks without creating a backup
EOF
}

backup_if_exists() {
    local target="$1"
    if [[ -f "${target}" ]]; then
        local backup
        backup="${target}.bak.$(date +%Y%m%d%H%M%S)"
        mv "${target}" "${backup}"
        echo "Backed up existing hook -> ${backup}"
    fi
}

render_hook() {
    local template="$1" dest="$2"
    if [[ ! -f "${template}" ]]; then
        echo "ERROR: template not found: ${template}" >&2
        exit 1
    fi
    # `|` as sed delimiter avoids collisions with `/` in filesystem paths.
    # The substituted values are paths under the repo root, which never
    # contain `|` on this project, so this is safe.
    sed \
        -e "s|__REPO_ROOT__|${REPO_ROOT}|g" \
        -e "s|__VENV__|${VENV}|g" \
        "${template}" > "${dest}"
    chmod +x "${dest}"
}

install_hooks() {
    if (( FORCE == 0 )); then
        backup_if_exists "${PRE_COMMIT}"
        backup_if_exists "${PRE_PUSH}"
    fi

    render_hook "${TEMPLATES_DIR}/pre-commit.template" "${PRE_COMMIT}"
    echo "Installed hook: pre-commit"

    render_hook "${TEMPLATES_DIR}/pre-push.template" "${PRE_PUSH}"
    echo "Installed hook: pre-push"

    echo "Git hooks installation completed"
}

uninstall_hooks() {
    local removed=0

    for hook in pre-commit pre-push; do
        local target="${HOOKS_DIR}/${hook}"
        if [[ -f "${target}" ]]; then
            rm -f "${target}"
            echo "Removed hook: ${hook}"
            (( removed++ )) || true
        else
            echo "Hook not installed: ${hook}"
        fi
    done

    if (( removed > 0 )); then
        echo "Git hooks uninstallation completed"
    fi
}

# Argument parsing — supports `install|uninstall` plus `--force` in any order.
ACTION="install"
ACTION_SET=0
for arg in "$@"; do
    case "${arg}" in
        install|uninstall)
            ACTION="${arg}"
            ACTION_SET=1
            ;;
        --force)
            FORCE=1
            ;;
        -h|--help|help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown argument: ${arg}" >&2
            usage
            exit 1
            ;;
    esac
done
: "${ACTION_SET}"  # silence unused-var lints; default action is install

case "${ACTION}" in
    install)
        install_hooks
        ;;
    uninstall)
        uninstall_hooks
        ;;
esac
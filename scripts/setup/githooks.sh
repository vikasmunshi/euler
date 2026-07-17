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

# The venv whose flake8/mypy the rendered hooks call — identified from the ambient
# ``python``, i.e. the shell's answer to ``sys.executable``, rather than guessed from a
# path.
#
# That is what makes one render correct everywhere. The operator's terminal answers with
# this checkout's ``.venv``; a collaborator's web shell answers with ``/opt/euler/venv``,
# which is right — a provisioned clone has no ``.venv`` of its own, and its hooks must
# call the deployed venv, exactly as ``user.sh`` § provision_hooks renders them. Both
# answers come from ``solver.config._enter_root``, which puts the running interpreter's
# bin dir at the head of ``PATH``, so any shell descended from a solver shell names its
# own venv. Assuming ``${REPO_ROOT}/.venv`` instead is what gave a clone hooks pointing at
# a venv that was never there: every commit and push then died on "No such file or
# directory" — the checks did not pass or fail, they could not run at all.
#
# Probed in order:
#   EULER_VENV        — an explicit override, taken strictly: set means use it or fail.
#   command -v python — the ambient venv, whenever this runs inside one.
#   REPO_ROOT/.venv   — the fresh-install case: `make install-all` builds the venv and
#                       installs the hooks in one breath, from a shell whose PATH predates
#                       that venv and so cannot name it.
# A candidate counts only if it is really a venv: a bin/python AND a pyvenv.cfg.
is_venv() {
    local dir="$1"
    [[ -n "${dir}" && -x "${dir}/bin/python" && -f "${dir}/pyvenv.cfg" ]]
}

# The venv root of the ambient ``python``, or empty. Deliberately NOT symlink-resolved:
# a venv's bin/python points at the system interpreter it was built from, so following it
# would report /usr and lose the venv we were asked to find.
ambient_venv() {
    local py
    py="$(command -v python 2>/dev/null)" || return 0
    (cd "$(dirname "${py}")/.." 2>/dev/null && pwd) || return 0
}

resolve_venv() {
    local candidate
    for candidate in "${EULER_VENV:-}" "$(ambient_venv)" "${REPO_ROOT}/.venv"; do
        if is_venv "${candidate}"; then
            echo "${candidate}"
            return 0
        fi
    done
    return 0  # nothing usable; the caller reports it (install fatal, status descriptive)
}

if [[ -n "${EULER_VENV:-}" ]] && ! is_venv "${EULER_VENV}"; then
    echo "ERROR: EULER_VENV=${EULER_VENV} is not a venv (needs bin/python and pyvenv.cfg)." >&2
    exit 1
fi
VENV="$(resolve_venv)"

FORCE=0

usage() {
    cat <<EOF
Usage: $0 [install|uninstall|status|cleanup] [--force]

  install      Write git hooks into .git/hooks/
  uninstall    Remove the managed hooks from .git/hooks/
  status       Show installed hooks: present, current vs stale, venv, backups (default)
  cleanup      Remove rotated hook backups (.bak.*) after confirmation
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
    if [[ -z "${VENV}" ]]; then
        echo "ERROR: no venv found — '$(command -v python || echo python)' is not one, and there is" >&2
        echo "       no ${REPO_ROOT}/.venv. The hooks run a venv's flake8/mypy, so there is" >&2
        echo "       nothing to install against. Run this from a solver shell or an activated venv," >&2
        echo "       build the dev venv ('make install-all'), or set EULER_VENV to one that exists." >&2
        exit 1
    fi

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

# One status line per hook: present or not, and — by comparing against a fresh
# render of its template with the resolved VENV — whether the installed copy is
# current or stale (template changed, or rendered against a different venv).
status_hooks() {
    local hook target installed_venv fresh
    for hook in pre-commit pre-push; do
        target="${HOOKS_DIR}/${hook}"
        if [[ ! -f "${target}" ]]; then
            echo "${hook}:  ✗ not installed (run '$0 install')"
            continue
        fi
        installed_venv="$(sed -n 's/^VENV="\(.*\)"$/\1/p' "${target}" | head -n1)"
        # A hook whose venv is gone cannot run its checks at all — a louder problem than
        # staleness, and the one the reader must act on, so it is reported first.
        if [[ -n "${installed_venv}" && ! -x "${installed_venv}/bin/python" ]]; then
            echo "${hook}:  ✗ installed but BROKEN (venv ${installed_venv} is missing — re-run '$0 install')"
            continue
        fi
        fresh="$(sed -e "s|__REPO_ROOT__|${REPO_ROOT}|g" -e "s|__VENV__|${VENV}|g" \
                     "${TEMPLATES_DIR}/${hook}.template")"
        if [[ "$(cat "${target}")" == "${fresh}" ]]; then
            echo "${hook}:  ✓ installed, current (venv ${installed_venv:-?})"
        else
            echo "${hook}:  ⚠ installed but STALE (venv ${installed_venv:-?}; template or venv changed — re-run '$0 install')"
        fi
    done
    local backups
    backups=$(find "${HOOKS_DIR}" -maxdepth 1 -name '*.bak.*' 2>/dev/null | sort)
    if [[ -n "${backups}" ]]; then
        echo "backups:     $(wc -l <<< "${backups}") rotated hook backup(s) ('$0 cleanup' removes them):"
        sed 's/^/  /' <<< "${backups}"
    else
        echo "backups:     none"
    fi
}

# Remove the rotated .bak.* copies install leaves behind — with confirmation,
# since a backup may hold the only copy of a locally-customised hook.
cleanup_backups() {
    local backups reply
    backups=$(find "${HOOKS_DIR}" -maxdepth 1 -name '*.bak.*' 2>/dev/null | sort)
    if [[ -z "${backups}" ]]; then
        echo "No hook backups to remove."
        return 0
    fi
    echo "Hook backups in ${HOOKS_DIR}:"
    sed 's/^/  /' <<< "${backups}"
    read -r -p "Remove these $(wc -l <<< "${backups}") backup(s)? [y/N] " reply
    if [[ "${reply}" =~ ^[Yy]$ ]]; then
        xargs -d '\n' rm -f -- <<< "${backups}"
        echo "Hook backups removed."
    else
        echo "Keeping the backups."
    fi
}

# Argument parsing — supports `install|uninstall` plus `--force` in any order.
ACTION="status"
ACTION_SET=0
for arg in "$@"; do
    case "${arg}" in
        install|uninstall|status|cleanup)
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
: "${ACTION_SET}"  # silence unused-var lints; default action is status (read-only)

case "${ACTION}" in
    install)
        install_hooks
        ;;
    uninstall)
        uninstall_hooks
        ;;
    status)
        status_hooks
        ;;
    cleanup)
        cleanup_backups
        ;;
esac
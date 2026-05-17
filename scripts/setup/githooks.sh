#!/usr/bin/env bash
# Git Hooks Setup Script
# ======================
#
# This script installs or removes the project's git hooks by writing
# the hook scripts directly into .git/hooks/.
#
# Hooks managed:
#   - pre-commit  (.git/hooks/pre-commit)
#   - pre-push    (.git/hooks/pre-push)
#
# Author: Vikas Munshi <vikas.munshi@gmail.com>
# Copyright (c) 2024. All rights reserved.
# Licensed under the MIT License.

set -euo pipefail
declare DIR_TO_CHECK SOLUTIONS_DIR

REPO_ROOT="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)"
HOOKS_DIR="${REPO_ROOT}/.git/hooks"

PRE_COMMIT="${HOOKS_DIR}/pre-commit"
PRE_PUSH="${HOOKS_DIR}/pre-push"

VENV="${REPO_ROOT}/.venv"

usage() {
    echo "Usage: $0 [install|uninstall]"
    echo
    echo "  install     Write git hooks into .git/hooks/ (default)"
    echo "  uninstall   Remove the managed hooks from .git/hooks/"
}

install_pre_commit() {
    tee "${PRE_COMMIT}" <<'EOF' > /dev/null
#!/usr/bin/env bash
set -euo pipefail

EOF
    { printf 'REPO_ROOT="%s"\n' "${REPO_ROOT}"
      printf 'VENV="%s"\n' "${VENV}" ;} >> "${PRE_COMMIT}"
    tee -a "${PRE_COMMIT}" <<'EOF' > /dev/null
cd "$REPO_ROOT"
failed=0

# trailing-whitespace: auto-fix staged .py files, then re-stage
py_files=$(git diff --cached --name-only --diff-filter=d -- '*.py')
if [[ -n "$py_files" ]]; then
    echo "$py_files" | xargs sed -i 's/[[:space:]]*$//'
    echo "$py_files" | xargs git add
fi

# trailing-whitespace: check staged changes (exclude encrypted files)
if ! git diff --check --cached --no-color -- ':!*.enc' 2>&1; then
    failed=1
fi

# flake8: run on staged .py files only
py_files=$(git diff --cached --name-only --diff-filter=d -- '*.py')
if [[ -n "$py_files" ]]; then
    if ! echo "$py_files" | xargs "$VENV/bin/flake8"; then
        failed=1
    fi
fi

# mypy: always run on solver
if ! "$VENV/bin/mypy" solver; then
    failed=1
fi

exit $failed
EOF
    chmod +x "${PRE_COMMIT}"
    echo "Installed hook: pre-commit"
}

install_pre_push() {
    tee "${PRE_PUSH}" <<'EOF' > /dev/null
#!/usr/bin/env bash
# Native pre-push hook. Runs for every push.
# Checks:
#   1. No commit in the push range contains files under euler/.
#   2. No un_enc_files .py/.c/.json solution files for problems > 100.
#   3. flake8 on .py files changed in the push range.
#   4. mypy on solver (always).
set -euo pipefail

EOF
    { printf 'REPO_ROOT="%s"\n' "${REPO_ROOT}"
      printf 'VENV="%s"\n' "${VENV}"
      printf 'DIR_TO_CHECK="%s"\n' "${DIR_TO_CHECK}"
      printf 'SOLUTIONS_DIR="%s"\n' "${SOLUTIONS_DIR}" ;} >> "${PRE_PUSH}"
    tee -a "${PRE_PUSH}" <<'EOF' > /dev/null
cd "$REPO_ROOT"
ZERO="0000000000000000000000000000000000000000"

# Capture stdin — git passes one line per ref: <local-ref> <local-sha> <remote-ref> <remote-sha>
stdin_data=$(cat)
failed=0
py_files_all=""

while IFS=' ' read -r _local_ref local_sha _remote_ref remote_sha; do
    [[ "$local_sha" == "$ZERO" ]] && continue  # deleted ref, nothing to check

    if [[ "$remote_sha" == "$ZERO" ]]; then
        # New branch: check all commits on this ref
        commits=$(git rev-list "$local_sha")
        range="$local_sha"
    else
        commits=$(git rev-list "$remote_sha..$local_sha")
        range="$remote_sha..$local_sha"
    fi

    for commit in $commits; do
        # 1. workspace (DIR_TO_CHECK) directory check — per commit
        files=$(git ls-tree -r --name-only "$commit" -- "$DIR_TO_CHECK" 2>/dev/null)
        if [[ -n "$files" ]]; then
            echo "ERROR: commit $(git log -1 --pretty='%h %s' "$commit") contains files under '$DIR_TO_CHECK/':" >&2
            echo "  ${files//$'\n'/$'\n'  }" >&2
            failed=1
        fi

        # 2. Unencrypted solution files for problems > 100 — per commit
        un_enc_files=$(git diff-tree --no-commit-id -r --name-only --diff-filter=d "$commit" -- \
            "$SOLUTIONS_DIR/" 2>/dev/null \
            | grep -E '\.(py|c|json)$' \
            | grep -v -E '^solutions/0/0/|^solutions/0/1/0/0/' \
            || true)
        if [[ -n "$un_enc_files" ]]; then
            echo "ERROR: commit $(git log -1 --pretty='%h %s' "$commit") adds unencrypted files for problem > 100:" >&2
            echo "  ${un_enc_files//$'\n'/$'\n'  }" >&2
            failed=1
        fi
    done

    # Collect .py files changed in this ref's range (for flake8 below)
    changed=$(git diff --name-only --diff-filter=d "$range" -- '*.py' 2>/dev/null || true)
    if [[ -n "$changed" ]]; then
        py_files_all+=$'\n'"$changed"
    fi

done <<< "$stdin_data"

# 3. flake8 on all .py files changed across pushed refs (deduplicated)
if [[ -n "$py_files_all" ]]; then
    unique_py=$(echo "$py_files_all" | sort -u | grep -v '^$')
    if ! echo "$unique_py" | xargs "$VENV/bin/flake8"; then
        failed=1
    fi
fi

# 4. mypy on solver (run once)
if ! "$VENV/bin/mypy" solver; then
    failed=1
fi

exit $failed
EOF
    chmod +x "${PRE_PUSH}"
    echo "Installed hook: pre-push"
}

install_hooks() {
    DIR_TO_CHECK=$(${VENV}/bin/python - <<'EOF'
from solver.core.config import Config
from solver.utils.path_utils import canonical_path
print(canonical_path(Config.workspace_dir))
EOF
)
    if [[ -z "${DIR_TO_CHECK}" || ! -d "${REPO_ROOT}/${DIR_TO_CHECK}" ]]; then
        echo "ERROR: DIR_TO_CHECK is not a valid directory: '${DIR_TO_CHECK}'" >&2
        exit 1
    fi

    SOLUTIONS_DIR=$(${VENV}/bin/python - <<'EOF'
from solver.core.config import Config
from solver.utils.path_utils import canonical_path
print(canonical_path(Config.solutions_dir))
EOF
)
    if [[ -z "${SOLUTIONS_DIR}" || ! -d "${REPO_ROOT}/${SOLUTIONS_DIR}" ]]; then
        echo "ERROR: SOLUTIONS_DIR is not a valid directory: '${SOLUTIONS_DIR}'" >&2
        exit 1
    fi

    install_pre_commit
    install_pre_push
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

# Main execution
# Defaults to 'install' if no argument provided
ACTION="${1:-install}"

case "${ACTION}" in
    install)
        install_hooks
        ;;
    uninstall)
        uninstall_hooks
        ;;
    -h|--help|help)
        usage
        ;;
    *)
        echo "Unknown action: ${ACTION}"
        usage
        exit 1
        ;;
esac

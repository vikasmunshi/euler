#!/usr/bin/env bash
# Script to safely reset Git repository history to initial commit
# and optionally force push changes to remote repository
# Setting options to exit on
#   non-zero return value (-e),
#   error on unset variables (-u),
#   and error on pipe failures (-o pipefail)
#   printing commands as they execute (-x)
set -euox pipefail

# Exit codes
readonly E_NOT_GIT_REPO=1
readonly E_BACKUP_FAILED=2
readonly E_PRE_COMMIT_FAILED=3
readonly E_SOLVER_FAILED=4
readonly E_UNLOCKED_FILES=5

# Repository configuration
readonly BRANCH_NAME="master"
declare BACKUP_DIR
BACKUP_DIR="/tmp/git-backup-$(date +%Y%m%d_%H%M%S)"
readonly BACKUP_DIR

# Ensure clean exit
trap 'echo "Script interrupted. Exiting..."; exit 1' INT TERM

# Validate git repository
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit ${E_NOT_GIT_REPO}

# Validate all solutions compute against dev test cases (use dev cases for speed)
solver 0 --d || exit ${E_SOLVER_FAILED}

# Create backup
git bundle create "${BACKUP_DIR}.bundle" --all || exit ${E_BACKUP_FAILED}
echo "Backup created at: ${BACKUP_DIR}.bundle"

read -p "Are you sure you want to reset Git history to initial commit? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[yY]$ ]]; then
    git reset --soft "$(git rev-list --max-parents=0 HEAD)"
fi

# unlock files for pre-commit run
solver 0 --unlock
git add -A
# run pre-commit checks on plain-text content of all files
pre-commit run --all || exit ${E_PRE_COMMIT_FAILED}
# lock files after pre-commit run
solver 0 --lock
git add -A
# run pre-commit checks on cypher-text content of all files
pre-commit run --all || exit ${E_PRE_COMMIT_FAILED}
solver 0 --summary
git add README.md
git commit -m "framework, templates, and solutions rev $(date +%Y%m%d)" >/dev/null
git prune

set +x
# Find Python and C files for problems 101 and above and list only those that don't contain 'encrypted'
declare -a unlocked_files=()
while IFS= read -r file; do
    if ! grep -q "encrypted" "$file" 2>/dev/null; then
        unlocked_files+=("$file")
    fi
done < <(find . -type f \( -name "p[0-9][1-9][0-9][0-9].py" -o -name "p[0-9][1-9][0-9][0-9].c" \) | grep -v p0100)
readonly unlocked_files
if [ ${#unlocked_files[@]} -ne 0 ]; then
    echo "Error: Unlocked files found"
    echo "${unlocked_files[@]}"
    exit ${E_UNLOCKED_FILES}
fi
set -x

read -p "Do you want to force push and override remote history? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[yY]$ ]]; then
    git push origin "${BRANCH_NAME}" -f
else
    git push origin "${BRANCH_NAME}"
fi

echo "Operation completed successfully"
echo "Backup location: ${BACKUP_DIR}.bundle"


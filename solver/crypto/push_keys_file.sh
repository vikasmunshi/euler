#!/usr/bin/env bash
set -e  # Exit on error

# This script pushes known_keys file to a new branch and creates a PR
# Required environment variables:
#   USER_ID: email address of the user
#   BRANCH_NAME: name of the branch to create
#   FILE_TO_PUSH: absolute path to the keys.json file

# Validate required environment variables
if [[ -z "${USER_ID}" ]] || [[ -z "${BRANCH_NAME}" ]] || [[ -z "${FILE_TO_PUSH}" ]]; then
    echo "Error: Required environment variables not set"
    echo "Required: USER_ID, BRANCH_NAME, FILE_TO_PUSH"
    exit 1
fi

# Check if gh CLI is authenticated
if ! gh auth status >/dev/null 2>&1; then
    echo "GitHub CLI is not authenticated. Please run: gh auth login"
    exit 2
fi

# Configure git to use gh as credential helper for this push
git config --local --unset-all credential.helper 2>/dev/null || true
git config --local --add credential.helper "!gh auth git-credential"

# Save current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Cleanup function to restore state
cleanup() {
    git checkout "${CURRENT_BRANCH}" 2>/dev/null || true
    git stash pop 2>/dev/null || true
}

# Set trap to ensure cleanup on exit
trap cleanup EXIT

# Add known_keys to staging so it can be stashed
git add "${FILE_TO_PUSH}"

# Stash all changes including staged files
git stash push -m "temp stash for ${BRANCH_NAME}"

# Delete branch if it exists
git branch -D "${BRANCH_NAME}" 2>/dev/null || true

# Create and checkout branch
git checkout -b "${BRANCH_NAME}"

# Apply only the known_keys file from stash
git checkout "stash@{0}" -- "${FILE_TO_PUSH}"

# Commit only the known_keys file
git commit -m "Add known keys for ${USER_ID}"

# Push the branch (force push to overwrite if exists)
git push -f origin "${BRANCH_NAME}"

echo "Successfully pushed known keys for ${USER_ID} to branch ${BRANCH_NAME}"

# Create pull request
PR_TITLE="Add known keys for ${USER_ID}"
PR_BODY="This PR adds the public key for ${USER_ID} to the known_keys file.

- User: ${USER_ID}
- Branch: ${BRANCH_NAME}

Please review and merge."

if gh pr create --title "${PR_TITLE}" --body "${PR_BODY}" --base master --head "${BRANCH_NAME}"; then
    echo "Pull request created successfully!"
else
    echo "Failed to create pull request. You can manually create one for branch: ${BRANCH_NAME}"
fi

#!/usr/bin/env bash
set -e  # Exit on error

user_email=$(git config user.email)
if [[ -z "${user_email}" ]]; then
  echo "Error: could not get user email"
  exit 1
fi

branch_name="keys_json_file_for_${user_email//[^a-zA-Z0-9._-]/_}"
file_to_push="$(dirname "${BASH_SOURCE[0]}")/keys.json"

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
git add "${file_to_push}"

# Stash all changes including staged files
git stash push -m "temp stash for ${branch_name}"

# Delete branch if it exists
git branch -D "${branch_name}" 2>/dev/null || true

# Fetch to ensure origin/master is current before branching
git fetch origin master

# Create and checkout branch from origin/master so local commits are not included
git checkout -b "${branch_name}" origin/master

# Apply only the known_keys file from stash
git checkout "stash@{0}" -- "${file_to_push}"

# Commit only the known_keys file
git commit -m "Add/update public key for ${user_email}"

# Push the branch (force push to overwrite if exists)
git push -f origin "${branch_name}"

echo "Successfully pushed keys.json for ${user_email} to branch ${branch_name}"

# Create pull request
PR_TITLE="Add/update public key for ${user_email}"
PR_BODY="This PR adds the public key for ${user_email} to the keys.json file.

- User: ${user_email}
- Branch: ${branch_name}

Please review and merge."

if gh pr create --title "${PR_TITLE}" --body "${PR_BODY}" --base master --head "${branch_name}"; then
    echo "Pull request created successfully!"
else
    echo "Failed to create pull request. You can manually create one for branch: ${branch_name}"
fi

#!/usr/bin/env bash
set -e  # Exit on error

# Check if gh CLI is authenticated
if ! gh auth status >/dev/null 2>&1; then
    echo "GitHub CLI is not authenticated. Please run: gh auth login"
    exit 1
fi

method=$1
# Validate method argument
if [[ "${method}" != "push" && "${method}" != "pull" ]]; then
  echo "Error: method must be either 'push' or 'pull', got: '${method}'"
  exit 2
fi

# Get repository owner's email from GitHub
get_repo_owner_email() {
  local repo_owner
  local owner_email
  repo_owner=$(gh repo view --json owner --jq '.owner.login')
  if [[ -z "${repo_owner}" ]]; then
    echo "Error: could not get repository owner"
    exit 3
  fi
  owner_email=$(gh api "users/${repo_owner}" --jq '.email')
  if [[ -z "${owner_email}" ]]; then
    echo "Error: could not get owner email"
    exit 4
  fi
  echo "${owner_email}"
}

# Get GitHub authenticated user's email
get_gh_user_email() {
  local gh_username
  local gh_user_email
  gh_username=$(gh api user --jq '.login')
  if [[ -z "${gh_username}" ]]; then
    echo "Error: could not get GitHub authenticated username"
    exit 5
  fi
  gh_user_email=$(gh api user --jq '.email')
  if [[ -z "${gh_user_email}" ]]; then
    echo "Error: could not get Githun authenticated user's email"
    exit 6
  fi
  echo "${gh_user_email}"
}

repo_owner_email=$(get_repo_owner_email)
user_email=$(get_gh_user_email)
# Check if method is push, then user_email must match repo owner's email
if [[ "${method}" == "push" && "${user_email}" != "${repo_owner_email}" ]]; then
  echo "Error: only repository owner (${repo_owner_email}) can use 'push' method, current user: '${user_email}'"
  exit 6
fi

# Configure git to use gh as credential helper for this push
current_credential_helper=$(git config --local --get credential.helper 2>/dev/null || echo "")
if [[ "${current_credential_helper}" != "!gh auth git-credential" ]]; then
    git config --local --unset-all credential.helper 2>/dev/null || true
    git config --local --add credential.helper "!gh auth git-credential"
fi

current_user_email=$(git config --local --get user.email 2>/dev/null || echo "")
if [[ "${current_user_email}" != "${user_email}" ]]; then
    git config --local user.email "${user_email}"
fi

desired_user_name="$(gh api user --jq '.name // .login')"
current_user_name=$(git config --local --get user.name 2>/dev/null || echo "")
if [[ "${current_user_name}" != "${desired_user_name}" ]]; then
    git config --local user.name "${desired_user_name}"
fi

branch_name="keys_json_file_updated_by_${user_email//[^a-zA-Z0-9._-]/_}"
file_to_push="$(dirname "${BASH_SOURCE[0]}")/../keys/keys.json"
# Save current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Cleanup function to restore state
cleanup() {
    git checkout "${CURRENT_BRANCH}" 2>/dev/null || true
    if [[ "${method}" == "push" ]]; then
      git pull || true
    fi
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

case "${method}" in
  push)
    # directly push ot master
    git push -f origin "${branch_name}":master
    echo "Successfully pushed keys.json updated by ${user_email} to origin master"
    ;;
  pull)
    # create a pull request
    git push -f origin "${branch_name}"
    echo "Successfully pushed keys.json updated by ${user_email} to branch ${branch_name}"
    # Create pull request (only for push method)
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
    ;;
esac


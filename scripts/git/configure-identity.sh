#!/usr/bin/env bash
set -e  # Exit on error

configure_identity() {
    # configure_identity — Configure gh as the git credential helper and set
    #                      git user.name / user.email from the gh logged-in user.
    #
    # Logs in via `gh auth login` if not yet authenticated (interactive), runs
    # `gh auth setup-git`, then reads the authenticated user's profile via
    # `gh api user`:
    #   - user.name  ← profile name, falling back to the login
    #   - user.email ← public profile email, falling back to the GitHub
    #                  noreply address <id>+<login>@users.noreply.github.com
    # The identity is written to the local (repository) git config.
    local login name email user_id

    gh auth status >/dev/null 2>&1 || gh auth login

    login=$(gh api user --jq .login)
    if [[ -z "${login}" ]]; then
        echo "Error: could not get GitHub authenticated username" >&2
        return 1
    fi

    name=$(gh api user --jq .name)
    if [[ -z "${name}" || "${name}" == "null" ]]; then
        name="${login}"
    fi

    email=$(gh api user --jq .email)
    if [[ -z "${email}" || "${email}" == "null" ]]; then
        user_id=$(gh api user --jq .id)
        email="${user_id}+${login}@users.noreply.github.com"
    fi

    gh auth setup-git
    git config user.name "${name}"
    git config user.email "${email}"

    printf "Git identity configured from gh user '%s':\n" "${login}"
    printf "  user.name:  %s\n" "${name}"
    printf "  user.email: %s\n" "${email}"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    configure_identity
fi
#!/usr/bin/env bash
set -e  # Exit on error

declare gh_user_email gh_user_name repo_owner_email repo_owner_name
init_gh_git_identity() {
    # init_gh_git_identity — Populate GitHub/repo identity globals and sync the
    #                        local git config identity to the authenticated user.
    #
    # Globals set (module-level, declared externally):
    #   gh_user_name      Login of the authenticated GitHub user
    #   gh_user_email     Email of the authenticated GitHub user
    #   repo_owner_name   Login of the current repo's owner
    #   repo_owner_email  Email of the current repo's owner
    #
    # Side effects (all local to the current git repo):
    #   git config user.name       — set to match the authenticated GitHub user
    #   git config user.email      — set to match the authenticated GitHub user
    #
    # Returns:
    #   0  All phases completed successfully
    #   1  gh CLI not authenticated; or one or more API fields could not be
    #      retrieved; or a git config write failed
    #
    # Phases (each is skipped if a prior phase fails):
    #   1. Fetch gh_user_name, gh_user_email, repo_owner_name, repo_owner_email
    #      via the GitHub API
    #   2. Sync local git identity (user.name, user.email) to the authenticated user
    #
    # Credential helper note:
    #   git auth is delegated to the gh CLI via a global, per-host credential
    #   helper configured once by `gh auth setup-git` (install-credentials
    #   Makefile target) — not by this function.
    #
    # Notes:
    #   - Requires `gh` CLI authenticated via `gh auth login`
    #   - Must be run inside a git repository
    #   - GitHub may return a null email if the user has hidden it in their profile,
    #     which will cause phase 1 to fail
    local rc=0
    if ! gh auth status >/dev/null 2>&1; then
        echo "GitHub CLI is not authenticated. Please run: gh auth login" >&2
        return 1 # no point in continuing, exit early
    fi
    gh_user_name=$(gh api user --jq '.login')
    if [[ -z "${gh_user_name}" ]]; then
        echo "Error: could not get GitHub authenticated username" >&2
        rc=1
    fi
    gh_user_email=$(gh api user --jq '.email')
    if [[ -z "${gh_user_email}" ]]; then
        echo "Error: could not get GitHub authenticated user's email" >&2
        rc=1
    fi
    repo_owner_name=$(gh repo view --json owner --jq '.owner.login')
    if [[ -z "${repo_owner_name}" ]]; then
        echo "Error: could not get repository owner" >&2
        rc=1
    fi
    repo_owner_email=$(gh api "users/${repo_owner_name}" --jq '.email')
    if [[ -z "${repo_owner_email}" ]]; then
        echo "Error: could not get owner email" >&2
        rc=1
    fi

    [[ ${rc} == 0 ]] || return ${rc} # must not continue to git config

    local git_user_email git_user_name
    git_user_email=$(git config --local --get user.email 2>/dev/null || echo "")
    if [[ "${git_user_email}" != "${gh_user_email}" ]]; then
        if ! git config --local user.email "${gh_user_email}"; then
            echo "Error: could not set git user email" >&2
            rc=1
        fi
    fi
    git_user_name=$(git config --local --get user.name 2>/dev/null || echo "")
    if [[ "${git_user_name}" != "${gh_user_name}" ]]; then
        if ! git config --local user.name "${gh_user_name}"; then
            echo "Error: could not set git user name" >&2
            rc=1
        fi
    fi

    # The git credential helper is configured globally via `gh auth setup-git`
    # (see the install-credentials Makefile target). Do not write a local
    # credential.helper here — it duplicates the global, per-host setup and
    # risks local/global drift.

    return ${rc}
}

check_not_gitignored() {
    # check_not_gitignored — Verify that none of the input paths are excluded by .gitignore.
    #
    # Usage: check_not_gitignored <path> [path ...]
    #
    # Returns:
    #   0  No input paths are gitignored
    #   1  One or more input paths are gitignored (offending paths printed to stderr)
    local ignored
    ignored=$(printf '%s\0' "$@" | git check-ignore -z --stdin 2>/dev/null | tr '\0' '\n') || true
    if [[ -n "${ignored}" ]]; then
        echo "Error: the following paths are excluded by .gitignore:" >&2
        printf '  %s\n' "${ignored}" >&2
        return 1
    fi
}

targets_are_valid() {
    # targets_are_valid — Verify that each target is an existing directory.
    #
    # Usage: targets_are_valid <dir> [dir ...]
    #
    # Returns:
    #   0  All targets are existing directories
    #   1  One or more targets are missing or not directories (offending paths printed to stderr)
    local rc=0 target
    for target in "${targets[@]}"; do
        if [[ ! -d "${target}" ]]; then
            echo "Error: target is not an existing directory: ${target}" >&2
            rc=1
        fi
    done
    return ${rc}
}

run_pre_commit_checks() {
    # run_pre_commit_checks — Run githooks/pre-commit and githooks/pre-push checks.
    #
    # Runs the two native git hooks directly (outside of a git operation) so that
    # publish can validate the working tree before committing and pushing.
    #
    # pre-push is invoked with stdin that mimics pushing the current HEAD to
    # origin/master, matching exactly what git sends during a real push.
    #
    # Returns:
    #   0  All hooks passed
    #   1  One or more hooks failed
    local rc=0

    if ! bash ./.git/hooks/pre-commit; then
        echo "Error: pre-commit checks failed; aborting publish" >&2
        rc=1
    fi

    local push_stdin
    push_stdin="refs/heads/master $(git rev-parse HEAD) refs/heads/master $(git rev-parse origin/master)"
    if ! echo "${push_stdin}" | bash ./.git/hooks/pre-push; then
        echo "Error: pre-push checks failed; aborting publish" >&2
        rc=1
    fi

    return ${rc}
}

ensure_targets_are_tracked() {
    # ensure_targets_are_tracked — Update the local git index to reflect the current
    #                              state of all target directories (new, modified, deleted).
    #
    # Usage: ensure_targets_are_tracked <dir> [dir ...]
    #
    # Returns:
    #   0  Index updated successfully
    #   1  git add failed
    git add -A -- "${targets[@]}"
}

publish() {
    # publish — Publish target directories to origin.
    #
    # Usage: publish
    #   Requires targets, gh_user_name, gh_user_email, repo_owner_email to be set
    #   (populated by init_gh_git_identity).
    #
    # Behaviour:
    #   - Fetches origin/master and resets HEAD to it (soft, preserving working tree)
    #   - Stages all target directories and creates a commit
    #   - If gh_user_email == repo_owner_email: pushes to origin/master directly
    #   - Otherwise: pushes to a named branch and opens a pull request
    #   - If dry_run=1: skips push and PR; prints the commands that would run instead
    #
    # Returns:
    #   0  Published (or PR created, or dry-run) successfully
    #   1  Commit, push, or PR creation failed
    git fetch origin master
    git reset --soft origin/master
    git add -A -- "${targets[@]}"

    if git diff --cached --quiet; then
        echo "Nothing to publish: no changes detected in targets" >&2
        return 0
    fi

    local targets_list commit_msg
    printf -v targets_list '%s, ' "${targets[@]}"
    commit_msg="Publish ${targets_list%, }; updated by ${gh_user_name} on $(date +%y%m%d)"
    git commit -m "${commit_msg}"
    echo "Created commit: ${commit_msg}"

    if [[ "${gh_user_email}" == "${repo_owner_email}" ]]; then
        eval_with_dry_run git push origin master
    else
        local branch_name
        branch_name="${gh_user_name}_$(date +%y%m%d)"
        eval_with_dry_run git push -f origin "HEAD:${branch_name}"
        if ! eval_with_dry_run gh pr create \
                --head "${branch_name}" \
                --base master \
                --title "Publish files updated by ${gh_user_name}" \
                --body "This PR publishes updated files from ${gh_user_name}."; then
            echo "Error: could not create pull request" >&2
        else
            echo "After the PR is merged, run: solver sync"
        fi
    fi
}

declare dry_run=0
eval_with_dry_run() {
    # eval_with_dry_run — Execute a command, or print it if dry_run=1.
    #
    # Usage: eval_with_dry_run <command> [arg ...]
    #   Pass the command and its arguments as separate words, exactly as you
    #   would invoke the command directly. In dry-run mode the expanded words
    #   are printed to stdout with a '[dry-run]' prefix instead of being executed.
    #
    # Returns:
    #   In normal mode: the exit code of the evaluated command
    #   In dry-run mode: 0 always
    local rc
    if [[ "${dry_run}" -eq 0 ]]; then
        "$@"
        rc=$?
        echo "$* -> ${rc}"
        return ${rc}
    else
        echo "[dry-run] $*"
    fi
}

usage() {
    cat >&2 <<EOF
Usage: $(basename "$0") [--dry-run] <dir> [dir ...]
       $(basename "$0") -h | --help

Publish local directories to origin/master.

Arguments:
  dir             Directory to publish. Must exist on disk.

Options:
  --dry-run       Run all steps except the final push and pull request.
                  Prints the git push and gh pr create commands that would
                  be executed.
  -h, --help      Show this help message and exit.

Behaviour:
  - Verifies no input paths are gitignored
  - Verifies each target is an existing directory
  - Syncs local git identity and credential helper to the authenticated gh user
  - Updates the local git index to track any new or deleted files in the targets
  - Fetches origin/master and resets HEAD to it (soft, preserving working tree)
  - Stages target directories and commits (message includes target list and yymmdd date)
  - If the authenticated user is the repo owner: pushes to origin/master directly
  - Otherwise: pushes to a named branch and opens a pull request
EOF
}

declare -a targets
main() {
    set -e
    [[ ${#targets[@]} -eq 0 ]] && { echo "Error: no targets specified" >&2; usage; exit 1; }
    mapfile -t targets < <(printf '%s\n' "${targets[@]}" | sort -u)
    check_not_gitignored "${targets[@]}"
    targets_are_valid
    init_gh_git_identity
    ensure_targets_are_tracked
    run_pre_commit_checks
    publish
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    [[ " $* " == *" -h "* || " $* " == *" --help "* ]] && { usage; exit 0; }
    [[ " $* " == *" --dry-run "* ]] && dry_run=1
    for _arg in "$@"; do [[ "${_arg}" != -* ]] && targets+=("${_arg}"); done
    main
fi

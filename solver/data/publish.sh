#!/usr/bin/env bash
set -e  # Exit on error

declare gh_user_email gh_user_name repo_owner_email repo_owner_name
init_gh_git_identity() {
    # init_gh_git_identity — Populate GitHub/repo identity globals, sync local git
    #                        config identity, and configure gh as the local git
    #                        credential helper.
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
    #   git config credential.helper — set to '!gh auth git-credential'
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
    #   3. Ensure credential.helper is set to delegate auth to gh CLI
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

    [[ ${rc} == 0 ]] || return ${rc} # no point in continuing to git auth setup

    local credential_helper
    local desired="!gh auth git-credential"
    credential_helper=$(git config --local --get credential.helper 2>/dev/null || echo "")
    if [[ "${credential_helper}" != "${desired}" ]]; then
        git config --local --unset-all credential.helper 2>/dev/null || true # ok to fail, if nothing is set
        if ! git config --local --add credential.helper "${desired}"; then
            echo "Error: could not set gh as git auth helper"
            rc=1
        fi
    fi

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

declare -a expanded_target_files
expand_target_files() {
    # expand_target_files — Resolve input paths to a concrete list of files.
    #
    # Usage: expand_target_files <path> [path ...]
    #
    # Globals set (module-level, declared externally):
    #   expanded_target_files  array — resolved file paths (relative to repo root);
    #                                  for file inputs: the file itself;
    #                                  for directory inputs: all tracked files plus
    #                                  all untracked non-gitignored files within
    #
    # Notes:
    #   - Does not modify the index or worktree
    #   - Untracked files excluded by .gitignore are omitted (run check_not_gitignored
    #     before this function if gitignored inputs should be an error)
    #
    # Returns:
    #   0  At least one file resolved successfully
    #   1  A path does not exist, or no files were found in the specified paths
    expanded_target_files=()
    local path
    for path in "$@"; do
        if [[ ! -e "${path}" ]]; then
            echo "Error: path does not exist: ${path}" >&2
            return 1
        fi
        if [[ -f "${path}" ]]; then
            expanded_target_files+=("${path}")
        elif [[ -d "${path}" ]]; then
            local -a dir_files=()
            mapfile -t dir_files < <(git ls-files -- "${path}" 2>/dev/null)
            expanded_target_files+=("${dir_files[@]+"${dir_files[@]}"}")
            mapfile -t dir_files < <(git ls-files --others --exclude-standard -- "${path}" 2>/dev/null)
            expanded_target_files+=("${dir_files[@]+"${dir_files[@]}"}")
        fi
    done
    if [[ ${#expanded_target_files[@]} -eq 0 ]]; then
        echo "Error: no files found in the specified paths" >&2
        return 1
    fi
}

declare -a changed_target_files
get_changed_target_files() {
    # get_changed_target_files — Fetch from origin and identify which target files
    #                            differ from origin/master.
    #
    # Usage: get_changed_target_files <file> [file ...]
    #   Files should be the output of expand_target_files (concrete file paths,
    #   relative to repo root).
    #
    # Globals set (module-level, declared externally):
    #   changed_target_files  array — files from the input that differ from
    #                                 origin/master (worktree, index, or new)
    #
    # Notes:
    #   - Fetches origin/master; requires network access
    #   - Does not modify the index or worktree
    #   - New (untracked) files are always included — they do not exist on origin/master
    #
    # Returns:
    #   0  Comparison completed (changed_target_files may be empty)
    #   1  git fetch failed
    local -a files=("$@")

    if ! git fetch origin master 2>/dev/null; then
        echo "Error: could not fetch from origin" >&2
        return 1
    fi

    changed_target_files=()

    local -a tracked=() untracked=()
    local f
    for f in "${files[@]}"; do
        if git ls-files --error-unmatch -- "${f}" &>/dev/null; then
            tracked+=("${f}")
        else
            untracked+=("${f}")
        fi
    done

    # Untracked files are new relative to origin/master — always include them
    changed_target_files+=("${untracked[@]+"${untracked[@]}"}")

    if [[ ${#tracked[@]} -gt 0 ]]; then
        local diff_output
        diff_output=$(
            {
                git diff --name-only origin/master -- "${tracked[@]}" 2>/dev/null
                git diff --name-only --cached origin/master -- "${tracked[@]}" 2>/dev/null
            } | sort -u
        )
        if [[ -n "${diff_output}" ]]; then
            local -a diff_files
            mapfile -t diff_files <<< "${diff_output}"
            changed_target_files+=("${diff_files[@]}")
        fi
    fi
}

publish_files() {
    # publish_files — Publish changed files to origin via a temporary local branch.
    #
    # Usage: publish_files <file> [file ...]
    #   Files should be the output of get_changed_target_files.
    #   Requires gh_user_name, gh_user_email, repo_owner_email to be set
    #   (populated by init_gh_git_identity).
    #
    # Behaviour:
    #   - Creates a local branch "${gh_user_name}_$(date +%y%m%d)" from origin/master
    #     in a temporary git worktree (current branch and index are untouched)
    #   - Copies target files into the worktree and commits them
    #   - If gh_user_email == repo_owner_email: force-pushes to origin/master directly
    #   - Otherwise: pushes to origin/<branch> and opens a pull request
    #   - Cleans up the worktree and local branch on exit (including on error)
    #   - If dry_run=1: skips push and PR; prints the commands that would run instead
    #
    # Returns:
    #   0  Files published (or PR created, or dry-run) successfully
    #   1  Worktree setup, push, or PR creation failed
    local -a files=("$@")
    local branch_name
    local worktree_path
    branch_name="${gh_user_name}_$(date +%y%m%d)"
    worktree_path=$(mktemp -d)

    git branch -D "${branch_name}" 2>/dev/null || true
    git worktree add "${worktree_path}" -b "${branch_name}" origin/master

    # Double-quote expansion bakes the current values into the trap string so
    # they remain accessible after publish_files returns and locals go out of scope.
    # shellcheck disable=SC2064
    trap "
        git worktree remove --force '${worktree_path}' || true
        git branch -D '${branch_name}' || true
    " EXIT

    local f
    for f in "${files[@]}"; do
        cp --parents "${f}" "${worktree_path}/"
    done

    git -C "${worktree_path}" add -- "${files[@]}"

    # Run pre-commit against the target files. Hooks may auto-fix files and exit
    # non-zero on the first run; re-stage and retry once to allow for that.
    if ! ( cd "${worktree_path}" && pre-commit run --files "${files[@]}" ); then
        git -C "${worktree_path}" add -- "${files[@]}"
        if ! ( cd "${worktree_path}" && pre-commit run --files "${files[@]}" ); then
            echo "Error: pre-commit checks failed; fix the issues and re-run" >&2
            return 1
        fi
    fi

    local files_list
    printf -v files_list '%s, ' "${target_files[@]}"
    git -C "${worktree_path}" commit -m "Publish ${files_list%, }; updated by ${gh_user_name} on $(date +%y%m%d)"

    if [[ "${gh_user_email}" == "${repo_owner_email}" ]]; then
        eval_with_dry_run git -C "${worktree_path}" push -f origin "${branch_name}":master
        eval_with_dry_run git fetch origin master
        eval_with_dry_run git reset --soft origin/master
    else
        eval_with_dry_run git -C "${worktree_path}" push -f origin "${branch_name}"
        if ! eval_with_dry_run gh pr create \
                --head "${branch_name}" \
                --base master \
                --title "Publish files updated by ${gh_user_name}" \
                --body "This PR publishes updated files from ${gh_user_name}."; then
            echo "Error: could not create pull request" >&2
            return 1
        fi
        echo "After the PR is merged, run: solver refresh"
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
Usage: $(basename "$0") [--dry-run] <path> [path ...]
       $(basename "$0") -h | --help

Publish changed local files to origin/master.

Arguments:
  path            File or directory to publish. Directories are expanded to
                  all tracked and untracked (non-gitignored) files within.

Options:
  --dry-run       Run all steps except the final push and pull request.
                  Prints the git push and gh pr create commands that would
                  be executed.
  -h, --help      Show this help message and exit.

Behaviour:
  - Verifies no input paths are gitignored
  - Expands directories to their constituent files
  - Compares target files against origin/master; exits 0 if nothing has changed
  - Syncs local git identity and credential helper to the authenticated gh user
  - Creates a temporary local branch from origin/master in a git worktree,
    copies changed files into it, and commits (message includes yymmdd)
  - If the authenticated user is the repo owner: force-pushes to origin/master
  - Otherwise: pushes to a named branch and opens a pull request
  - Cleans up the worktree and local branch on exit
  - Syncs current branch to origin/master with reset --soft (owner path only)
EOF
}

declare -a target_files
main() {
    target_files=("$@")
    if [[ ${#target_files[@]} -eq 0 ]]; then
        echo "Error: no files or directories specified" >&2
        usage
        exit 1
    fi

    check_not_gitignored "${target_files[@]}" || exit 1
    expand_target_files "${target_files[@]}" || exit 2
    get_changed_target_files "${expanded_target_files[@]}" || exit 3

    if [[ ${#changed_target_files[@]} -eq 0 ]]; then
        echo "Nothing to publish: no changes detected relative to origin/master"
        exit 0
    fi

    init_gh_git_identity || exit 4
    publish_files "${changed_target_files[@]}" || exit 5
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    [[ " $* " == *" -h "* || " $* " == *" --help "* ]] && { usage; exit 0; }
    [[ " $* " == *" --dry-run "* ]] && dry_run=1
    declare -a _args=()
    for _arg in "$@"; do [[ "${_arg}" != -* ]] && _args+=("${_arg}"); done
    main "${_args[@]}"
fi

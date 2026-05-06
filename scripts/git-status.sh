#!/usr/bin/env bash
set -e  # Exit on error

declare summary=0

show_sync_status() {
    # show_sync_status — Display commit divergence between local HEAD and origin/master.
    #
    # Fetches origin/master then prints:
    #   - Number of commits ahead / behind
    #   - Overall sync state
    local ahead behind state

    if ! git fetch origin master 2>/dev/null; then
        echo "Error: could not fetch from origin" >&2
        return 1
    fi

    ahead=$(git rev-list --count origin/master..HEAD)
    behind=$(git rev-list --count HEAD..origin/master)

    if   [[ ${ahead} -eq 0 && ${behind} -eq 0 ]]; then
        state="up to date"
    elif [[ ${ahead} -gt 0 && ${behind} -eq 0 ]]; then
        state="local ahead"
    elif [[ ${ahead} -eq 0 && ${behind} -gt 0 ]]; then
        state="local behind"
    else
        state="diverged"
    fi

    printf "Sync with origin/master: %s\n" "${state}"
    printf "  ahead:  %d commit(s)\n" "${ahead}"
    printf "  behind: %d commit(s)\n" "${behind}"

    if [[ ${ahead} -gt 0 ]]; then
        local local_commits
        local_commits=$(git log --oneline origin/master..HEAD)
        echo "  local commits:"
        echo "    ${local_commits//$'\n'/$'\n    '}"
    fi
    if [[ ${behind} -gt 0 ]]; then
        local origin_commits
        origin_commits=$(git log --oneline HEAD..origin/master)
        echo "  origin commits:"
        echo "    ${origin_commits//$'\n'/$'\n    '}"
    fi
}

show_committed_diff() {
    # show_committed_diff — List files committed locally that differ from origin/master.
    #   With summary=1: prints the count instead of the full list.
    local files
    files=$(git diff --name-only origin/master HEAD 2>/dev/null)
    echo "Files committed locally vs origin/master:"
    if [[ -z "${files}" ]]; then
        echo "  (none)"
    elif [[ "${summary}" -eq 0 ]]; then
        echo "  ${files//$'\n'/$'\n  '}"
    else
        echo "  $(echo "${files}" | wc -l | tr -d ' ') file(s)"
    fi
}

show_uncommitted_changes() {
    # show_uncommitted_changes — List staged and unstaged changes in the worktree.
    #                            Untracked files are excluded.
    #   With summary=1: prints the count instead of the full list.
    echo "Uncommitted changes (staged/unstaged):"
    local changes
    changes=$(git status --short --untracked-files=no)
    if [[ -z "${changes}" ]]; then
        echo "  (none)"
    elif [[ "${summary}" -eq 0 ]]; then
        echo "  ${changes//$'\n'/$'\n  '}"
    else
        echo "  $(echo "${changes}" | wc -l | tr -d ' ') file(s)"
    fi
}


main() {
    show_sync_status
    echo
    show_committed_diff
    echo
    show_uncommitted_changes
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    [[ " $* " == *" --summary "* ]] && summary=1
    main
fi

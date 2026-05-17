#!/usr/bin/env bash
set -e  # Exit on error

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

main() {
    # main — Fetch origin/master, determine sync state, and bring local in sync.
    #
    # State detection:
    #   up_to_date   — local HEAD == origin/master
    #   local_ahead  — local has commits not on origin/master (publish first)
    #   local_behind — origin/master has commits not in local HEAD
    #   diverged     — both sides have commits the other does not
    #
    # Sync strategy by state:
    #   up_to_date   — nothing to do
    #   local_ahead  — warn; no auto-sync (use 'solver publish <target>')
    #   local_behind — git merge --ff-only origin/master
    #                  (stash/unstash uncommitted changes if present)
    #   diverged     — git rebase origin/master
    #                  (stash/unstash uncommitted changes if present)
    local ahead behind has_changes state

    git fetch origin master 1>/dev/null 2>&1
    ahead=$(git rev-list --count origin/master..HEAD)
    behind=$(git rev-list --count HEAD..origin/master)

    if git diff --quiet 2>/dev/null && git diff --cached --quiet 2>/dev/null; then
        has_changes=0
    else
        has_changes=1
    fi

    if   [[ ${ahead} -eq 0 && ${behind} -eq 0 ]]; then
        state="up_to_date"
    elif [[ ${ahead} -gt 0 && ${behind} -eq 0 ]]; then
        state="local_ahead"
    elif [[ ${ahead} -eq 0 && ${behind} -gt 0 ]]; then
        state="local_behind"
    else
        state="diverged"
    fi

    local changes_msg
    [[ ${has_changes} -eq 1 ]] && changes_msg="uncommitted changes present" || changes_msg="clean worktree"
    echo "State: ${state} (ahead: ${ahead}, behind: ${behind}, ${changes_msg})"

    case "${state}" in
        up_to_date)
            echo "Action: nothing to do."
            ;;
        local_ahead)
            echo "Action: no sync — use 'solver publish <target>' to publish to origin."
            echo "Warning: local has ${ahead} commit(s) ahead of origin/master. No sync performed."
            echo "  Use 'solver publish <target>' to publish file changes to origin."
            ;;
        local_behind)
            echo "Action: fast-forward merge from origin/master${has_changes:+; stash/unstash around merge}."
            if [[ ${has_changes} -eq 1 ]]; then
                eval_with_dry_run git stash push -m "refresh: stash before sync"
                eval_with_dry_run git merge --ff-only origin/master
                eval_with_dry_run git stash pop
            else
                eval_with_dry_run git merge --ff-only origin/master
            fi
            ;;
        diverged)
            echo "Action: rebase local commits onto origin/master${has_changes:+; stash/unstash around rebase}."
            echo "Warning: local has diverged (${ahead} ahead, ${behind} behind)."
            echo "  Replaying local commits on top of origin/master via rebase."
            if [[ ${has_changes} -eq 1 ]]; then
                eval_with_dry_run git stash push -m "refresh: stash before rebase"
                eval_with_dry_run git rebase origin/master
                eval_with_dry_run git stash pop
            else
                eval_with_dry_run git rebase origin/master
            fi
            ;;
    esac
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    [[ " $* " == *" --dry-run "* ]] && dry_run=1
    main
fi

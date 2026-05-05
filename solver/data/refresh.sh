#!/usr/bin/env bash
set -e  # Exit on error

# shellcheck source=status.sh
source "$(dirname "${BASH_SOURCE[0]}")/status.sh"
# shellcheck source=publish.sh
source "$(dirname "${BASH_SOURCE[0]}")/publish.sh"

declare ahead=0 behind=0 has_changes=0 state=""
get_state() {
    # get_state — Compute sync state from already-fetched origin/master refs.
    #             Must be called after show_sync_status (which does the fetch).
    #
    # Globals set (module-level, declared externally):
    #   ahead        integer — commits local HEAD has that origin/master does not
    #   behind       integer — commits origin/master has that local HEAD does not
    #   has_changes  integer — 1 if worktree has staged/unstaged changes; 0 otherwise
    #   state        string  — up_to_date | local_ahead | local_behind | diverged
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
}

refresh() {
    # refresh — Bring local in sync with origin/master using the safest strategy.
    #
    # Strategy by state:
    #   up_to_date   — nothing to do
    #   local_ahead  — warn; suggest publish.sh; no auto-sync (would risk history loss)
    #   local_behind — git merge --ff-only origin/master
    #                  (stash uncommitted changes around it if needed)
    #   diverged     — git rebase origin/master (replays local commits on top)
    #                  (stash uncommitted changes around it if needed)
    #
    # In all stash/unstash cases a named stash is used so it can be recovered
    # manually if something goes wrong mid-sync.
    case "${state}" in
        up_to_date)
            echo "Nothing to do: local is up to date with origin/master."
            ;;
        local_ahead)
            echo "Warning: local has ${ahead} unpublished commit(s) not on origin/master."
            echo "  Run solver publish to push them. No automatic sync performed."
            ;;
        local_behind)
            if [[ ${has_changes} -eq 1 ]]; then
                eval_with_dry_run git stash push -m "refresh: stash before sync"
                eval_with_dry_run git merge --ff-only origin/master
                eval_with_dry_run git stash pop
            else
                eval_with_dry_run git merge --ff-only origin/master
            fi
            ;;
        diverged)
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


main() {
    # show_sync_status fetches origin/master; get_state reads the result without
    # a second fetch.
    export summary=1
    show_sync_status
    echo
    show_committed_diff
    echo
    show_uncommitted_changes
    echo
    get_state
    refresh
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    [[ " $* " == *" --dry-run "* ]] && export dry_run=1
    main
fi

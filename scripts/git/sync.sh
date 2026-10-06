#!/usr/bin/env bash
# Bring the local repository in sync with origin/master.
#
# Every failure is REPORTED, not fatal: this script returns a non-zero code and
# leaves the decision to its caller — `git-sync` (solver/utils/scripts.py), which
# gates the enc-key pull flow on it, and scripts/setup/user.sh, which treats a
# refused sync as a note and carries on provisioning. `set -e` could not serve
# either: it exited on the first failed git command, so the caller learned only
# "something failed", and — worse — the stash restore below never ran.
set -uo pipefail

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

verb_in_progress() {
    # verb_in_progress — True when a `git <verb>` stopped part-way and still owns the tree.
    #
    # Usage: verb_in_progress <verb>
    #   Reads the state files git itself writes, so it answers for a merge/rebase this
    #   script started OR one it inherited. An atomic failure (a refused --ff-only, say)
    #   leaves none of them and is correctly reported as 'not in progress' — nothing to
    #   roll back, and no spurious `--abort` to fail noisily.
    local verb="$1" gitdir
    gitdir=$(git rev-parse --git-dir 2>/dev/null) || return 1
    case "${verb}" in
        rebase) [[ -d "${gitdir}/rebase-merge" || -d "${gitdir}/rebase-apply" ]] ;;
        merge)  [[ -f "${gitdir}/MERGE_HEAD" ]] ;;
        *)      return 1 ;;
    esac
}

sync_onto_master() {
    # sync_onto_master — Run `git <verb> [arg ...]`, stashing a dirty tree around it.
    #
    # Usage: sync_onto_master <has_changes> <verb> [arg ...]
    #   verb is the git subcommand ('merge', 'rebase') — named, not baked into the
    #   command words, because the rollback below has to invoke `git <verb> --abort`.
    #   has_changes only decides whether to ATTEMPT a stash; whether one exists to pop
    #   afterwards is read back from refs/stash, never assumed from it.
    #
    # NEVER leaves the repository half-synced. A merge/rebase that fails usually stops
    # MID-WAY, on a conflicted index, so any failure is rolled back with `--abort`: the
    # tree ends up as it was found, always, whether or not it was dirty. This is a
    # deliberate trade against git's interactive habit of leaving a conflicted rebase in
    # progress to resolve — nothing here is interactive. `git-sync` is one step of a
    # shell command, and scripts/setup/user.sh runs it unattended while provisioning,
    # where the vault is locked and the smudge filter makes failure the expected case.
    # A caller that must resolve conflicts by hand can still drive git directly.
    #
    # The rollback also has to come FIRST, before the stash is restored: `git stash pop`
    # refuses to write over unmerged entries, so popping onto a conflicted index fails
    # and strands the changes in a stash nothing told the user about.
    #
    # Returns:
    #   The exit code of the sync command — the pop's code only when the pop is the
    #   thing that failed, since a completed sync whose stash will not pop is still a
    #   failure the caller must hear about.
    local has_changes="$1" verb="$2"; shift 2
    local rc stashed=0 stash_before stash_ours=''

    stash_before=$(git rev-parse -q --verify refs/stash)
    if [[ ${has_changes} -eq 1 ]]; then
        eval_with_dry_run git stash push -m "refresh: stash before ${verb}" || return $?
        # What was stashed, not what looked dirty: `git stash push` exits 0 whether or
        # not it created an entry ('No local changes to save'), so popping on the
        # strength of has_changes alone failed a sync that had already succeeded.
        stash_ours=$(git rev-parse -q --verify refs/stash)
        [[ "${stash_ours}" != "${stash_before}" ]] && stashed=1
    fi

    eval_with_dry_run git "${verb}" "$@"
    rc=$?

    if [[ ${rc} -ne 0 ]] && verb_in_progress "${verb}"; then
        echo "Error: 'git ${verb} $*' stopped part-way (${rc}) — rolling it back." >&2
        if ! eval_with_dry_run git "${verb}" --abort; then
            echo "Error: 'git ${verb} --abort' FAILED — the repository is still mid-${verb}." >&2
            echo "  Resolve it by hand: 'git ${verb} --abort', then 'git stash pop' if you had changes." >&2
            return ${rc}
        fi
    fi

    if [[ ${stashed} -eq 1 ]]; then
        if ! eval_with_dry_run git stash pop; then
            [[ ${rc} -eq 0 ]] && rc=1
            # A pop that conflicts does not fail atomically: it stages what applied cleanly,
            # marks the rest unmerged (UU), and KEEPS the stash entry. Left there, the clone is
            # wedged — HEAD is level with origin, so every later sync reports "nothing to do"
            # over a conflicted index, and the next stash it takes re-captures that half-state.
            # Everything the pop touched is still in the stash, and before the pop the tracked
            # tree was exactly HEAD, so resetting to HEAD loses nothing — but only while the
            # stash entry is still the one this run pushed, which is checked, not assumed.
            if [[ "$(git rev-parse -q --verify refs/stash)" == "${stash_ours}" ]] &&
                eval_with_dry_run git reset --hard -q HEAD; then
                echo "Error: synced, but your uncommitted changes conflict with the incoming work." >&2
                echo "  The tree is left clean at HEAD; your changes are safe in stash@{0}." >&2
                echo "  Inspect with 'git stash show -p', re-apply with 'git stash pop' and resolve" >&2
                echo "  the conflicts by hand — or discard them with 'git stash drop'." >&2
            else
                echo "Error: your changes are safe but still STASHED, and the tree may be part-applied." >&2
                echo "  Recover them with 'git stash pop' after resolving by hand — 'git-reset --hard'" >&2
                echo "  returns to origin/master but DISCARDS the stash along with everything else." >&2
            fi
        fi
    fi
    return ${rc}
}

main() {
    # main — Fetch origin/master and tags, prune dead remote branches, and bring local in sync.
    #
    # State detection:
    #   up_to_date   — local HEAD == origin/master
    #   local_ahead  — local has commits not on origin/master (publish first)
    #   local_behind — origin/master has commits not in local HEAD
    #   diverged     — both sides have commits the other does not
    #
    # Sync strategy by state:
    #   up_to_date   — nothing to do
    #   local_ahead  — warn; no auto-sync (use 'solver git-push')
    #   local_behind — git merge --ff-only origin/master
    #                  (stash/unstash uncommitted changes if present)
    #   diverged     — git rebase origin/master
    #                  (stash/unstash uncommitted changes if present)
    #
    # Returns:
    #   0 when the repository is in sync, or was deliberately left alone
    #     (up_to_date, local_ahead — declining to sync is not a failure)
    #   1 when the state could not be determined, the clone is mid-merge (unmerged
    #     paths, or a merge/rebase in progress), or the sync itself failed
    local ahead behind has_changes state prune_out unmerged
    local -a unmerged_paths

    # Fetch master. This one must succeed — it is the sync.
    if ! git fetch origin master 1>/dev/null 2>&1; then
        echo "Error: could not fetch origin/master." >&2
        return 1
    fi

    # Then the tags, SEPARATELY and best-effort. The version mechanism reads release tags
    # — the `version` command's `git describe` and release.sh's last-tag anchor — but a
    # normal fetch only auto-follows tags pointing at objects downloaded this time, so a
    # clone that already has the tagged commit never picks up its `vX.Y.Z` tag.
    #
    # `--force --prune-tags`: origin is the source of truth for release tags, so the clone
    # mirrors it. This used to be a plain `--tags` on the fetch above, on the reasoning
    # that release tags are immutable — until a history rewrite moved one. git then
    # refuses to clobber the local tag, `fetch` exits non-zero, and the whole sync failed
    # with it: every clone stuck, permanently, on a tag. For a reader that is terminal —
    # `git-sync` is the only git verb they have. A tag is bookkeeping; it must never be
    # able to fail the sync, so a failure here is a note, exactly like the prune below.
    if ! git fetch --tags --force --prune-tags origin 1>/dev/null 2>&1; then
        echo "Note: could not refresh tags (version reporting may be stale)." >&2
    fi

    # Drop remote-tracking refs for branches the remote no longer has — typically a
    # user/<slug> branch deleted when its pull request merged, which otherwise lingers
    # as a stale origin/<branch> and a '[gone]' upstream for as long as the clone lives.
    #
    # `git remote prune`, NOT `--prune` on the fetch above: prune only considers the
    # refs its refspec covers, and 'master' covers no user branch, so that fetch prunes
    # nothing. Widening the refspec to prune would drag every other collaborator's
    # branch into this clone just to notice one of its own is gone; pruning separately
    # removes the dead ref and adds none.
    #
    # Housekeeping, not sync: a prune that fails is noted, and the sync carries on.
    if [[ ${dry_run} -eq 1 ]]; then
        echo "[dry-run] git remote prune origin"
    elif prune_out=$(git remote prune origin 2>&1); then
        grep -F '[pruned]' <<<"${prune_out}" || true  # the 'URL:' heading is noise
    else
        echo "Note: could not prune stale remote-tracking refs — carrying on." >&2
    fi
    if ! ahead=$(git rev-list --count origin/master..HEAD 2>/dev/null) ||
        ! behind=$(git rev-list --count HEAD..origin/master 2>/dev/null); then
        echo "Error: could not compare HEAD with origin/master." >&2
        return 1
    fi

    # `git status`, not `git diff --quiet`: on the filtered tree (solutions/private/**,
    # filter=solver-crypt) `git diff` calls every one of those files changed — 'Binary
    # files differ' — on a tree that `git status` calls clean, that `git add -A` stages
    # nothing from, and that `git diff --cached` agrees is identical. Only git diff's
    # worktree comparison disagrees, and a preceding `git status` does not settle it.
    # Reading that as "uncommitted changes present" stashed a clean tree before every
    # sync. `git status` is both the correct answer and the one `git-status` prints,
    # so the two commands can no longer contradict each other.
    if [[ -z "$(git status --porcelain --untracked-files=no 2>/dev/null)" ]]; then
        has_changes=0
    else
        has_changes=1
    fi

    # A clone left mid-operation — unmerged (UU) paths from a conflicted stash pop or merge,
    # or a merge/rebase that never finished — is not "uncommitted changes": a stash refuses
    # it, and when HEAD happens to be level with origin the states below would report
    # "nothing to do" over a conflicted index, forever. Name it and stop; the way out
    # discards local changes, so it is the user's call, not this script's.
    unmerged=$(git diff --name-only --diff-filter=U 2>/dev/null)
    if [[ -n "${unmerged}" ]] || verb_in_progress merge || verb_in_progress rebase; then
        echo "Error: this clone is mid-merge — a merge, rebase or stash pop stopped part-way." >&2
        if [[ -n "${unmerged}" ]]; then
            mapfile -t unmerged_paths <<<"${unmerged}"
            printf '  unmerged: %s\n' "${unmerged_paths[@]}" >&2
        fi
        echo "  Nothing was synced. To return to origin/master, DISCARDING uncommitted changes and stashes:" >&2
        echo "    git-reset --hard" >&2
        echo "  Or resolve the conflicts by hand ('git status' shows them), then run git-sync again." >&2
        return 1
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
            echo "Action: no sync — use 'solver git-push' to publish to origin."
            echo "Warning: local has ${ahead} commit(s) ahead of origin/master. No sync performed."
            echo "  Use 'solver git-push' to push file changes to origin."
            ;;
        local_behind)
            echo "Action: fast-forward merge from origin/master${has_changes:+; stash/unstash around merge}."
            sync_onto_master "${has_changes}" merge --ff-only origin/master || return $?
            ;;
        diverged)
            echo "Action: rebase local commits onto origin/master${has_changes:+; stash/unstash around rebase}."
            echo "Warning: local has diverged (${ahead} ahead, ${behind} behind)."
            echo "  Replaying local commits on top of origin/master via rebase."
            sync_onto_master "${has_changes}" rebase origin/master || return $?
            ;;
    esac
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    [[ " $* " == *" --dry-run "* ]] && dry_run=1
    main
    exit $?
fi

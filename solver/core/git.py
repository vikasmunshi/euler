#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Git and GitHub (gh) commands and helpers — the repository workflow.

Per-user native git (docs/web-server-guide.md § Git): a collaborator's shell runs in
**their own clone** on branch `user/<slug>` as their own uid, so git needs no
broker — the read verbs (`git-status`, `git-sync`) are `reader`-floor and the
write verbs (`git-commit`, `git-push`, `git-hooks`) plus the tree audit
(`git-audit`) are `contributor`-floor; the blast radius is their own branch.
`master` stays gated: `gh-merge` (`maintainer`) is the one gate through which
a `user/<slug>` branch lands on master, and it opens only for a pull request whose every
file sits inside the allowlist (:data:`PR_SCOPE`).

`git-commit` is the **one** commit verb, and what it stages is named by its targets
(:data:`TARGET_PATHS`) rather than by a command per body of work: `solution` for the
problem the shell is on, `solutions` for the whole tree, and `docs` / `topics` / `update`
for the three path sets the doc-maintaining commands write — `update-docs` writes `docs/`
and the `update` set, `update-tags` writes both legs of the tag graph under `topics`, and
`update-models` / `update-usd-rate` write the `update` set. Targets compose, so a regeneration lands as one
reviewable commit that carries nothing else (`git-commit docs update`), and `--amend`
folds a fix into it rather than growing a commit behind it.

The gate reads from the same table: :data:`PR_SCOPE` is the union of :data:`TARGET_PATHS`,
so a pull request may carry whatever `git-commit` could have staged — several commits,
spanning several targets — and nothing else. There is one commit verb and one merge verb,
and the second admits exactly what the first can produce.
"""
from __future__ import annotations

__all__ = ['commit_regenerated', 'enc_key_arrived', 'get_gh_user_email', 'get_repo_owner_email',
           'git_commit', 'key_waiting_hint', 'merge_pr_for_branch', 'private_local_edits',
           'private_tree_opens', 'resmudge_private', 'git_reset', 'git_publish', 'git_status',
           'git_filter', 'git_sync', 'git_identity', 'git_push', 'gh_merge', 'git_hooks', 'git_audit']

import json
import random
import shlex
import sys
from collections.abc import Sequence
from datetime import datetime
from functools import lru_cache
from pathlib import PurePosixPath
from subprocess import run
from typing import Annotated, Any, Literal

from cryptography.exceptions import InvalidTag

from solver.config import ExitCodes, config
from solver.core import osc
from solver.core.problems import Problem
from solver.crypto.ciphers import decrypt_blob, is_encrypted, read_master_key
from solver.crypto import wire
from solver.crypto.gitfilter import filter_settings
from solver.shell import console, register
from solver.shell.dialogue import Ask, Choice
from solver.utils.shell_utils import run_cmdline, run_command
from solver.web.msg import PR_REVIEW_SUBJECT


# ── GitHub identity (gh) ────────────────────────────────────────────────────────────────

@lru_cache(maxsize=None)
def get_gh_user_email() -> str:
    """Return the authenticated GitHub user's email, cached after the first lookup."""
    is_authenticated: str | None = run_command('gh auth status')
    if not is_authenticated:
        raise ValueError('Error: gh CLI is not authenticated')
    username: str | None = run_command('gh api user --jq .login')
    if not username:
        raise ValueError('Error: could not get GitHub authenticated username')
    user_email: str | None = run_command('gh api user --jq .email')
    if not user_email or user_email == 'null':
        raise ValueError("Error: could not get GitHub authenticated user's email")
    return user_email


@lru_cache(maxsize=None)
def get_repo_owner_email() -> str:
    """Return the GitHub repository owner's email, cached after the first lookup."""
    repo_owner: str | None = run_command('gh repo view --json owner --jq .owner.login')
    if not repo_owner:
        raise ValueError('Error: could not get repository owner')
    owner_email: str | None = run_command(f'gh api users/{repo_owner} --jq .email')
    if not owner_email:
        raise ValueError('Error: could not get owner email')
    return owner_email


# ── what a commit stages ────────────────────────────────────────────────────────────────

#: What each `git-commit` target stages, as repo-relative git pathspecs. Three entry
#: forms — a trailing `/` is a directory prefix, an entry with `*` is a glob, anything
#: else is an exact path — read both by :func:`_pathspecs` (for git) and by
#: :func:`_in_scope` (for the merge gates), so one table answers "what does this commit
#: touch?" and "what may this pull request touch?".
#:
#: The `solution` target is absent because it is not a fixed set: it is *this* problem's
#: directory plus the progress file, which :func:`_solution_paths` derives per call.
#:
#: - `solutions` — the whole solution tree, tag legs and progress file included.
#: - `docs` — the guides, generated blocks and all (`update-docs`).
#: - `topics` — **both** legs of the tag graph: the articles and tag vocabulary under
#:   `topics/`, and each problem's `tags.json` (`update-tags`). They are one double-entry
#:   record, so splitting them across two commits is what this target exists to prevent —
#:   and it is the only thing this target reaches inside `solutions/`.
#: - `update` — everything else the `update-*` verbs write, wherever it
#:   happens to live: the README plus its generated package-layout block and the web start
#:   page's slice of it, the module registry, the managed settings (of which
#:   `update-usd-rate` writes the FX rate), the `# GEN:models` block, and the Claude guidance the root
#:   `CLAUDE.md` symlink points at. Source code by file type, generated data by content —
#:   which is why it is a target of its own and not part of `docs`.
TARGET_PATHS: dict[str, tuple[str, ...]] = {
    'solutions': ('solutions/',),
    'docs': ('docs/',),
    'topics': ('topics/', 'solutions/**/tags.json'),
    'update': ('README.md', 'solver/modules.csv', 'solver/config/values.conf', 'solver/ai/models.py',
               'solver/ai/claude/CLAUDE.md', 'solver/web/content/home-summary.md'),
}

#: What each `update-*` verb commits for itself (:func:`commit_regenerated`) — **exactly** the
#: paths that verb writes, which is why this is its own table and not the `docs`/`update`
#: targets above. Those targets are for a person naming a body of work: `update` deliberately
#: spans everything the four verbs write, so `git-commit docs update` lands a whole
#: regeneration as one reviewable commit. An automatic commit has nobody looking, so it must
#: not sweep up a sibling verb's uncommitted output — `update-models` staging the `update` set
#: would carry off a stale `values.conf` that `update-usd-rate` had not committed yet.
#:
#: Note `solver/ai/claude/CLAUDE.md` rather than the root `CLAUDE.md`: the root name is a
#: gitignored symlink onto it, so the tracked path is the target's.
GENERATED_PATHS: dict[str, tuple[str, ...]] = {
    'update-docs': ('docs/', 'README.md', 'solver/modules.csv',
                    'solver/ai/claude/CLAUDE.md', 'solver/web/content/home-summary.md'),
    'update-models': ('solver/ai/models.py',),
    'update-tags': ('topics/', 'solutions/**/tags.json'),
    'update-usd-rate': ('solver/config/values.conf',),
}


def _in_scope(path: str, scope: tuple[str, ...]) -> bool:
    """Whether *path* is inside *scope*: `dir/` by prefix, `a/**/b` by glob, else exactly.

    The exact and glob forms are what keep a scope narrow: `solver/config/values.conf` admits
    that one file and never the `solver/` tree around it, and `solutions/**/tags.json` admits a
    problem's tag leg without admitting the solution beside it.
    """
    for entry in scope:
        if entry.endswith('/'):
            if path.startswith(entry):
                return True
        elif '*' in entry:
            if PurePosixPath(path).full_match(entry):
                return True
        elif path == entry:
            return True
    return False


def _pathspecs(scope: tuple[str, ...]) -> list[str]:
    """*scope* as git pathspecs, in argv form (`shlex.quote` them for a shell command line).

    A glob entry is given git's explicit `:(glob)` magic so its `**` means what it means
    here — path-aware — rather than git's default wildmatch, where `*` also crosses `/`.
    """
    return [f':(glob){entry}' if '*' in entry else entry for entry in scope]


# ── commit ──────────────────────────────────────────────────────────────────────────────

def _current_branch() -> str:
    """The checked-out branch name ('' when detached or not a repo)."""
    proc = run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
               cwd=config.root_dir, capture_output=True, text=True)
    return proc.stdout.strip() if proc.returncode == 0 else ''


def _solution_paths(problem: Problem) -> tuple[str, ...]:
    """The `solution` target: *problem*'s own directory, and the progress file `mark` rewrites.

    Repo-relative, like every entry in :data:`TARGET_PATHS`: the pathspecs are handed to git
    with `cwd` at the repository root, and a `:(glob)` entry beside an absolute path would
    not mean what it says.
    """
    return (problem.solution_dir.relative_to(config.root_dir).as_posix(),
            config.static_file_problems.relative_to(config.root_dir).as_posix())


def _commit_paths(problem: Problem, targets: tuple[str, ...]) -> list[str]:
    """The git pathspecs *targets* stage for *problem*, de-duplicated in the order named.

    Targets overlap by design — `solutions` contains every `solution`, and `topics` reaches
    the tag leg inside the solution tree — so naming two that share a path must stage that
    path once, not twice.
    """
    specs: list[str] = []
    for target in targets:
        entries = TARGET_PATHS.get(target) or _solution_paths(problem)
        for spec in _pathspecs(entries):
            if spec not in specs:
                specs.append(spec)
    return specs


def _is_not_amend(bound: dict[str, Any]) -> bool:
    """Whether the commit is writing a new message — an amend keeps the one it has."""
    return not bound.get('amend', False)


@register(requires='contributor', aliases=('commit',), quietable=True)
def git_commit(problem: Problem,
               *targets: Literal['solution', 'solutions', 'docs', 'topics', 'update'],
               message: Annotated[str, Ask('Message', when=_is_not_amend, multiline=True)] = '',
               amend: bool = False,
               reset: bool = False,
               ) -> int:
    """Stage and commit the named targets — the one commit verb.

    The routine "save my progress" step. With no target it commits `solution`: everything
    under this problem's directory, plus `solutions/problems.json` (the progress file `mark`
    rewrites), and nothing else. Naming targets widens that to whichever bodies of work you
    mean, and they compose — `git-commit docs update` lands a whole `update-docs` run as one
    commit, `git-commit topics` lands both legs of the tag graph together. A target with
    nothing to stage contributes nothing rather than failing, so composing is cheap.

    `--amend` folds the same paths into HEAD with its message untouched — the "I forgot
    something" step, so a checkpoint absorbs the fix instead of growing a "fix typo" commit
    behind it. It is refused once HEAD is on origin (rewriting a pushed commit needs a
    force-push, so committing again is the honest step there), and is a no-op, not a failure,
    when those paths are clean. A message and `--amend` are mutually exclusive: exactly one
    of them says what the commit is called.

    Aliased as `commit`.

    Args:
        problem: [problem] The problem whose solution directory the `solution` target
            stages. Ignored by every other target.
        *targets: What to stage — 'solution' (this problem plus the progress file),
            'solutions' (the whole solution tree), 'docs' (the guides), 'topics' (the
            articles and every problem's tag leg) or 'update' (what the `update-*` verbs
            write outside `docs/` — the README, the module registry, the managed settings,
            the model block, the Claude guidance). Defaults to 'solution'.
        message: [asked] The commit message. Required unless `amend` is set, and asked for
            at the prompt when it is left out.
        amend: Fold the staged changes into HEAD instead of committing, keeping its
            message. Defaults to False. Refused with a message, with `reset`, or once
            HEAD is pushed.
        reset: Soft-reset to `origin/master` first, so the new commit squashes all local
            commits into a single checkpoint (the working tree is untouched). Defaults to
            False. `git-reset` is the same move without the re-commit.
    """
    if amend and message:
        console.print('[error]error:[/error] [accent]--amend[/accent] keeps HEAD\'s message — '
                      'drop the message, or commit without [accent]--amend[/accent].')
        return ExitCodes.EXIT_USAGE
    if amend and reset:
        console.print('[error]error:[/error] [accent]--reset[/accent] squashes the local commits into a '
                      'fresh one and [accent]--amend[/accent] folds into the last — pick one.')
        return ExitCodes.EXIT_USAGE
    if not amend and not message:
        # Only reachable non-interactively: at the prompt the `Ask` above collects it first.
        console.print('[error]error:[/error] a commit needs a message — pass '
                      '[accent]message=…[/accent], or [accent]--amend[/accent] to keep HEAD\'s.')
        return ExitCodes.EXIT_USAGE
    targets = targets or ('solution',)
    paths: list[str] = _commit_paths(problem, targets)
    dirty: str = run(['git', 'status', '--porcelain', '--', *paths],
                     cwd=config.root_dir, capture_output=True, text=True).stdout.strip()
    if amend:
        return _amend(paths, dirty, targets)
    # A clean target is nothing to do, not a failure — so this composes in a `&&` chain
    # after a regeneration (`update-docs && git-commit docs update`) that had nothing to
    # regenerate. `--reset` still runs: it is about squashing the local commits into one
    # checkpoint, which has nothing to do with the working tree.
    if not dirty and not reset:
        console.print(f'nothing to commit: [accent]{" ".join(targets)}[/accent] is unchanged.')
        return ExitCodes.EXIT_OK
    cmdline: list[str] = ['git', 'reset', '--soft', 'origin/master', '&&'] if reset else []
    cmdline += ['git', 'add', '-A', *(shlex.quote(spec) for spec in paths), '&&']
    cmdline += ['git', 'commit', '--message', shlex.quote(message)]
    result: int = run_cmdline(' '.join(cmdline))
    if result == 0:
        osc.git_changed()
    return result


def _amend(paths: list[str], dirty: str, targets: tuple[str, ...]) -> int:
    """Fold *paths* into HEAD with its message untouched — `git-commit --amend`.

    Three preconditions, each with its own diagnostic: there is a HEAD to amend, it is
    unpushed, and the paths are actually dirty (*dirty* being the caller's `git status`
    probe, which the plain commit needs anyway). The middle one is the reason this is a
    check and not just a git flag — amending rewrites the commit, and a rewritten commit
    already on origin only lands again through a force-push.
    """
    if run(['git', 'rev-parse', '--verify', '--quiet', 'HEAD'],
           cwd=config.root_dir, capture_output=True).returncode != 0:
        console.print('[error]error:[/error] no commit to amend.')
        return ExitCodes.EXIT_ERROR
    pushed: list[str] | None = _remotes_containing_head()
    if pushed is None:
        console.print('[error]error:[/error] cannot tell whether HEAD is pushed — not amending.')
        return ExitCodes.EXIT_ERROR
    if pushed:
        console.print(f'[error]error:[/error] HEAD is already pushed to [accent]{", ".join(pushed)}[/accent]; '
                      'amending it would need a force-push — commit without '
                      '[accent]--amend[/accent] instead.')
        return ExitCodes.EXIT_ERROR
    if not dirty:
        console.print(f'nothing to amend: [accent]{" ".join(targets)}[/accent] is unchanged.')
        return ExitCodes.EXIT_OK
    result: int = run_cmdline('git add -A ' + ' '.join(shlex.quote(spec) for spec in paths)
                              + ' && git commit --amend --no-edit')
    if result == 0:
        osc.git_changed()
    return result


def commit_regenerated(verb: str, quips: tuple[str, ...], detail: Sequence[str] = ()) -> int:
    """Commit what *verb* just regenerated — the `update-*` verbs' own commit.

    A regeneration that stops at the working tree leaves the next person to guess whether the
    diff is theirs, and leaves the git chip counting it as their uncommitted work. So each
    `update-*` verb lands its own output, staging exactly :data:`GENERATED_PATHS`\\ ``[verb]``
    and nothing beside it.

    The message is `chore(<verb>): <quip>` over a body naming what actually moved. The subject
    is deliberately a **`chore`**: `scripts/version/release.sh` derives the SemVer bump from
    the Conventional Commit types since the last tag, and regenerated docs, a re-scraped price
    table and an FX rate are none of them a feature — a `feat:` here would silently take the
    minor. The wit is the caller's (each verb knows its own subject); the facts are in the body,
    because a joke alone is a poor commit message.

    Clean paths are nothing to do, not a failure. A *failing* commit is returned as-is rather
    than swallowed: the files are already written, so re-running is idempotent, and a hook that
    rejected the commit is something to see rather than to hide behind a zero.
    """
    paths: list[str] = _pathspecs(GENERATED_PATHS[verb])
    dirty: str = run(['git', 'status', '--porcelain', '--', *paths],
                     cwd=config.root_dir, capture_output=True, text=True).stdout.strip()
    if not dirty:
        return ExitCodes.EXIT_OK
    body = '\n'.join([f'Regenerated by `{verb}`:', '', *(f'  {line}' for line in detail)]) if detail else ''
    message = f'chore({verb}): {random.choice(quips)}' + (f'\n\n{body}\n' if body else '\n')
    cmdline = ('git add -A ' + ' '.join(shlex.quote(spec) for spec in paths)
               + ' && git commit --message ' + shlex.quote(message))
    result: int = run_cmdline(cmdline)
    if result == 0:
        osc.git_changed()
    else:
        console.print(f'[warning]warning:[/warning] {verb} rewrote its files but the commit failed — '
                      'they are in the working tree, uncommitted.')
    return result


def _remotes_containing_head() -> list[str] | None:
    """The remote-tracking branches that contain HEAD — empty when it is local-only.

    Read from this clone's `origin/*` refs, which answer "have I pushed this?" — the one
    question an amend must ask. They are as fresh as the last fetch (`git-sync`); a commit
    pushed from *another* clone since then reads as local here, which is the residual risk
    the remote's own non-fast-forward rejection still catches.

    None when the question could not be answered at all (not a repo, no HEAD): the caller
    must refuse rather than read that as "not pushed".
    """
    proc = run(['git', 'branch', '--remotes', '--contains', 'HEAD', '--format', '%(refname:short)'],
               cwd=config.root_dir, capture_output=True, text=True)
    if proc.returncode != 0:
        return None
    # A bare '<remote>' among the refs is that remote's HEAD symref, not a branch it
    # carries — naming it alongside the branch it points at only pads the refusal.
    return [ref for line in proc.stdout.splitlines() if '/' in (ref := line.strip())]


def _commits_ahead_of_master() -> int:
    """How many local commits HEAD carries beyond `origin/master` (0 when unreadable).

    Read from HEAD, not `origin/<branch>`: this counts the commits a reset is about to
    undo, which live in *this* clone whether or not they ever reached the remote. Zero on
    any failure — a missing `origin/master`, a detached HEAD — since the reset that
    follows either no-ops or errors on its own, and this only sizes the report.
    """
    proc = run(['git', 'rev-list', '--count', 'origin/master..HEAD'],
               cwd=config.root_dir, capture_output=True, text=True)
    out: str = proc.stdout.strip()
    return int(out) if proc.returncode == 0 and out.isdigit() else 0


# Reader, alone among the verbs that move a ref: this one cannot lose work. `--soft` leaves
# the working tree untouched and makes no commit, so there is nothing it can destroy and
# nothing it can put on master — the blast radius that floors every other write verb is
# empty here. What the contributor floor did instead was strand the rung least able to help
# itself: a reader whose clone had drifted ahead of origin/master had no verb for it at all,
# which is a state they cannot reach by committing (they cannot) and so cannot be blamed for.
# `scripts/ops/reset-user.sh` stays the operator's answer for the harder wedge — a conflicted
# merge or a half-checked-out worktree needs `--hard`, which this deliberately is not.
@register(requires='reader', quietable=True, aliases=('reset',))
def git_reset() -> int:
    """Soft-reset your branch to origin/master — un-commit, keep every change.

    The undo `git-commit --reset` never lets you stop at: this runs
        `git reset --soft origin/master`, moving your branch tip back to origin/master
        while leaving the working tree untouched, so every local commit's changes survive
        as staged edits. From there re-commit differently (`git-commit`), restage
        selectively, or leave it — whereas `git-commit --reset` squashes straight into one
        fresh commit and gives you no such pause.

    Makes no commit, so it runs no hooks and is a clean no-op — exit 0 — when your branch
        is already level with origin/master. Undone commits are not lost: they stay
        reachable through the reflog until git eventually prunes them.

    Aliased as `reset`.
    """
    ahead: int = _commits_ahead_of_master()
    result: int = run_cmdline('git reset --soft origin/master')
    if result != 0:
        return result
    if ahead:
        console.print(f'[accent]{ahead}[/accent] commit(s) undone; your changes are kept, staged — '
                      'run [accent]git-commit[/accent] to re-commit.')
    else:
        console.print('already level with [accent]origin/master[/accent] — nothing to undo.')
    osc.git_changed()
    return int(ExitCodes.EXIT_OK)


# ── publish / status / sync / filter / identity ─────────────────────────────────────────

@register(requires='maintainer', aliases=('publish',), quietable=True)
def git_publish(*targets: Literal['scripts', 'solutions', 'solver'],
                dry_run: bool = False) -> int:
    """Publish changed files for named targets to the remote repository.

    Fails if any target is not one of the accepted scopes.

    Args:
        *targets: Scopes of files to publish — one or more of 'scripts', 'solutions' or
            'solver'. There is no `keys` scope: key material is not distributed by git any
            more. A holder's enc-key file is machine-local, and issuing one is
            `user-authorize` sending it through the message spool. Defaults to
            'solutions'.
        dry_run: Print the push and pull-request commands instead of running them.
            Defaults to False.
    """
    if not targets:
        targets = ('solutions',)
    if not all(target in ['scripts', 'solutions', 'solver'] for target in targets):
        raise ValueError(f'Invalid targets: {", ".join(targets)}')
    if dry_run:
        result = run_cmdline(f'{config.scripts.publish} --dry-run {" ".join(targets)}')
    else:
        result = run_cmdline(f'{config.scripts.publish} {" ".join(targets)}')
    if result == 0:
        osc.git_changed()
    return result


@register(requires='reader', aliases=('status',))
def git_status(details: bool = False) -> int:
    """Display the sync state between the local branch and origin/master.

    Reports how far ahead and behind your branch is, and what is uncommitted in the working
    tree — the read before deciding between `git-push`, `git-sync` and `git-commit`. It is
    as fresh as the last fetch; `git-sync` is what refreshes it. Aliased as `status`.

    Args:
        details: List every differing file and uncommitted change. Defaults to False, which
            shows file counts only.
    """
    if details:
        result = run_cmdline(config.scripts.status)
    else:
        result = run_cmdline(f'{config.scripts.status} --summary')
    return result


def resmudge_private() -> int:
    """Re-checkout `solutions/private` so stored ciphertext decrypts in place.

    Existing ciphertext in the worktree only decrypts on a *fresh* checkout, and git will not
    re-materialise a file it considers unchanged — hence the delete-then-checkout. That makes
    this destructive by construction, so it is guarded, and both callers share the guard:
    `git-filter install` (asked for explicitly) and :func:`enc_key_arrived` (after a key is
    saved) — neither may eat anyone's work.

    Genuine local edits are never clobbered — the re-checkout is skipped and says so. A
    freshly wired clone is NOT dirty (clean() passes ciphertext through, matching the stored
    blob), so the guard only trips on real plaintext changes.

    A **deletion** is not an edit anyone authored: it is the residue of exactly this operation
    having been interrupted — the `rm` lands, the checkout then fails (a filter that cannot
    decrypt makes it fail, since the rule is `required`), and the files are simply gone.
    Treating that as "local changes to protect" left a reader wedged, told to commit or stash,
    which names two verbs no reader has. The checkout restores deleted files, so let it.
    """
    dirty: str = run(['git', 'status', '--porcelain', '--', 'solutions/private'],
                     cwd=config.root_dir, capture_output=True, text=True).stdout.strip()
    lines = dirty.splitlines()
    deletions = [line for line in lines if line[:2] in (' D', 'D ', 'DD')]
    blocking = [line for line in lines if line not in deletions]
    if blocking:
        console.print('[warning]solutions/private has local changes — skipping the re-checkout; '
                      'commit or stash, then run [accent]git-filter install[/accent] again.[/warning]')
        return int(ExitCodes.EXIT_OK)
    if deletions:
        console.print(f'[muted]restoring [accent]{len(deletions)}[/accent] file(s) missing from the '
                      'worktree (an interrupted decrypt, not your edits)[/muted]')
    console.print('[primary]Decrypting private solutions in place...[/primary]')
    # Two steps, not one `&&` chain, so a failed checkout is reported as what it is: the
    # worktree is mid-way through the swap and the files are NOT there. Silence would leave
    # someone staring at an empty solutions/private with no idea it is recoverable.
    run_cmdline('git ls-files -z -- solutions/private | xargs -0 -r rm -f --')
    result = run_cmdline('git checkout -- solutions/private')
    if result != 0:
        console.print('[error]error:[/error] the re-checkout failed, so solutions/private is '
                      'currently EMPTY in your worktree. Nothing is lost — the content is in git. '
                      'Run [accent]git-filter install[/accent] again once the filter can decrypt.')
    return result


def private_local_edits() -> dict[str, bytes]:
    """The plaintext of every private file this worktree has changed, by path.

    **Call this while the key that opens HEAD is still the key in place** — it asks git for the
    diff, and git answers by running the clean filter over the worktree, so the answer is only
    truthful before a rotated key lands. Afterwards every private file reads as modified (the
    same plaintext encrypts to a different blob) and there is nothing left to tell a real edit
    from the rotation itself.

    Kept in memory, never spilled to a file: this is decrypted solution content, and the one
    place it is allowed to exist is the worktree it came from.

    A clone whose HEAD *already* does not open — wedged by an earlier rotation it never
    re-homed from — has no truthful answer to give, and the untruth is spectacular: with the
    held key not matching HEAD, every private file present cleans to a different blob and reads
    as an edit. That happened live, on a clone with no edits at all, and reported 917 of them —
    which the re-home would then have written back over the published tree as stale content.
    So the same test the re-home uses gates the question: no readable HEAD, no answer.
    """
    if not private_tree_opens():
        return {}
    # `git status`, not `git diff HEAD`. They disagree, and only one of them is answering the
    # question a person would recognise as theirs. Git does not run a clean filter on empty
    # content, so every empty `__init__.py` under this tree is 0 bytes in the worktree and 33
    # bytes of ciphertext in the commit: `git diff HEAD` compares those directly and calls all
    # 918 of them modified, for ever, on a pristine clone. Status compares through the index
    # and says what it is — clean. Live, that difference announced "kept your 917 local
    # edit(s)" to collaborators who had edited nothing.
    raw = run(['git', 'status', '--porcelain', '-z', '--', 'solutions/private'],
              cwd=config.root_dir, capture_output=True, text=True).stdout
    edits: dict[str, bytes] = {}
    tokens, index = raw.split('\0'), 0
    while index < len(tokens):
        entry, index = tokens[index], index + 1
        if not entry:
            continue
        if entry[0] in 'RC':  # a rename carries its source as the next NUL-separated token
            index += 1
        name = entry[3:]
        if (path := config.root_dir / name).is_file():
            edits[name] = path.read_bytes()
    return edits


def private_tree_opens(ref: str = 'HEAD') -> bool:
    """Whether *ref*'s private blobs decrypt under the master key this machine holds now.

    A rotation puts the key and the commits out of step, and **which** side is unreadable says
    what to do about it, so both get asked:

    - `HEAD` unreadable means the key is current and this clone's own history is not. That is
      worse than it looks — the worktree is fine, but *any* operation that materialises HEAD
      fails, `git stash` included, so `git-sync` cannot even begin its merge and the clone
      cannot sync its way out of being unsynced. The repair is :func:`_rehome_on_origin`.
    - `origin/master` unreadable means the opposite: this clone is coherent, holding an
      *old* key, and the published tree was re-encrypted without it. Nothing local can fix
      that — the new key is sitting in the message spool. Merging anyway is what produced a
      filter traceback and a half-applied merge on a live clone.

    Undecidable cases answer True. No such ref, no tracked private files, or nothing encrypted
    in the first handful all mean "nothing here says the tree is unreadable", and acting on
    silence would be the more destructive mistake.
    """
    tracked = run(['git', 'ls-files', '--', 'solutions/private'],
                  cwd=config.root_dir, capture_output=True, text=True).stdout.split()
    # Sample until an encrypted blob turns up rather than trusting the first name: a tracked
    # file the attributes do not match — anything added under this tree without the filter —
    # would otherwise answer "readable" for the whole tree, every time, and the answer gates
    # a repair. A handful of reads is enough; a tree with nothing encrypted in its first
    # dozen files is not one this check has anything to say about.
    for name in tracked[:12]:
        blob = run(['git', 'cat-file', 'blob', f'{ref}:{name}'],
                   cwd=config.root_dir, capture_output=True)
        if blob.returncode != 0 or not is_encrypted(blob.stdout):
            continue
        try:
            decrypt_blob(blob.stdout, read_master_key())
        except (FileNotFoundError, KeyError, ValueError, InvalidTag):
            return False
        return True
    return True


def key_waiting_hint() -> str:
    """The one line to show when this clone cannot read the published solutions — else ''.

    Both directions of a rotation end in the same instruction, because both are fixed by the
    same act: take the key a maintainer has already sent. Naming that is the whole point. The
    generic "run `git-sync` to see why" is a dead end here — `git-sync` is precisely what does
    not work — and it was what a collaborator actually saw at login while the answer sat unread
    in their spool.
    """
    if private_tree_opens('HEAD') and private_tree_opens('origin/master'):
        return ''
    waiting = ('a new master key is waiting for you — this clone cannot read the published '
               'solutions until you take it: ')
    # Point at whatever the reader is actually looking at. Over the web that is the envelope
    # chip in the header, whose key row carries its own [save] button, so nobody has to type a
    # message id they would have to go and find first. A terminal has no header — there, the
    # verbs are the only answer there is.
    if config.subject.channel == 'web':
        return waiting + ('open the [accent]✉ messages[/accent] menu in the header and press '
                          '[accent]save[/accent] on the master-key message.')
    return waiting + 'run [accent]msg list[/accent], then [accent]msg act <id>[/accent].'


def _rehome_on_origin(local_edits: dict[str, bytes]) -> bool:
    """Move a clone whose HEAD predates a rotation onto origin/master, keeping its edits.

    The only tree this machine's key opens is the one the rotation published, so the repair is
    to go there — `git reset --hard origin/master`, which is the one worktree-rewriting command
    that never has to materialise the unreadable HEAD on the way. Merging cannot do it (the
    stash resets to HEAD first), and neither can a re-checkout.

    *local_edits* is carried across as plaintext and written back afterwards, which works
    precisely because plaintext is key-agnostic: the same bytes re-encrypt cleanly under the
    new key on the next commit, and `git status` afterwards shows the same edits it showed
    before. They are the reason this is not simply reset-user.sh in Python.

    Unpushed commits stop it. Reset would orphan them, and for private paths their content is
    already encrypted under the retired key — unreadable to everyone, this machine included. So
    the clone is left exactly as it is and the situation is named, because quietly discarding
    work is worse than an error message, and this is the operator's to sort out.
    """
    if run_cmdline('git fetch --prune origin master') != 0:
        console.print('[error]error:[/error] the private solutions were re-encrypted under a new '
                      'key and this clone is still on the old tree, but origin is unreachable — '
                      'so the tree that matches your key cannot be fetched. Try again when the '
                      'network is back.')
        return False
    unpushed = run(['git', 'rev-list', '--count', 'origin/master..HEAD'],
                   cwd=config.root_dir, capture_output=True, text=True).stdout.strip()
    if unpushed not in ('', '0'):
        console.print(f'[warning]The master key was rotated, so this clone\'s history no longer '
                      f'decrypts — but it carries [accent]{unpushed}[/accent] commit(s) that are '
                      f'not on origin/master, and moving to the re-encrypted tree would orphan '
                      f'them.[/warning]\n[warning]Nothing has been changed. Ask a maintainer: any '
                      f'private content in those commits is encrypted under the retired key and '
                      f'has to be recovered before this clone can move.[/warning]')
        return False
    # Tags, best-effort and separately. A re-home lands on whatever origin/master is, which is
    # usually a release commit — and without its tag `git describe` reaches back to the last
    # tag the clone happens to hold, so `version` reported "3.2.4 / v3.2.2-8" about a clone
    # sitting exactly on v3.2.4. Separate because a moved tag makes the fetch exit non-zero
    # (`sync.sh` splits them for the same reason), and a stale tag must never block the repair.
    run_cmdline('git fetch --tags --force --prune-tags origin')
    console.print('[primary]The master key was rotated — moving this clone to the re-encrypted '
                  'tree on origin/master...[/primary]')
    if run_cmdline('git reset --hard origin/master') != 0:
        console.print('[error]error:[/error] could not reset onto origin/master; this clone still '
                      'cannot read its own history. Ask a maintainer to reset it.')
        return False
    for name, plaintext in local_edits.items():
        path = config.root_dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(plaintext)
    if local_edits:
        console.print(f'[muted]kept your [accent]{len(local_edits)}[/accent] local edit(s) to '
                      'solutions/private[/muted]')
    osc.git_changed()
    return True


def enc_key_arrived(local_edits: dict[str, bytes] | None = None) -> None:
    """Wire the git filter once this machine can decrypt — the tail of taking a key.

    A provisioned clone starts filter-UNWIRED with `solutions/private/**` as ciphertext.
    The moment the master key becomes readable — a maintainer issued it and `msg act` wrote
    it, or a rotation was carried across by `user --regen` — wire the clean/smudge filter and
    re-checkout the private tree, so ciphertext becomes plaintext in place.

    It used to hang off `git-sync`, because access arrived *through git*: the enc-key file was
    tracked, and a pull delivered it. Nothing about key material travels by git any more, so
    the trigger moved to the commands that actually change what this machine can open. A
    Also re-wires a clone whose recorded filter command has drifted from what `install`
    writes today — see below. A silent no-op while the wiring is current, or the key is not
    readable.

    Args:
        local_edits: the private worktree's edits, read by :func:`private_local_edits` *before*
            the key was written. Only a re-home needs them, and only the caller can collect
            them, because by the time this runs the old key is gone.
    """
    read_master_key.cache_clear()
    # Order matters: a key that arrived from a rotation leaves HEAD unreadable, and every
    # repair below materialises HEAD. Re-home first, or the re-checkout fails on the way.
    if not private_tree_opens():
        _rehome_on_origin(local_edits or {})
    name: str = wire.FILTER_NAME
    recorded = run(['git', 'config', '--local', '--get', f'filter.{name}.process'],
                   cwd=config.root_dir, capture_output=True, text=True)
    wanted = filter_settings(name)[f'filter.{name}.process']
    # Wired is not the same as wired CORRECTLY. A clone keeps whatever command was recorded
    # the day it was set up, so a change to that command — `-P`, most consequentially — never
    # reaches the clones that need it most: the ones already working, which stop working the
    # moment they fall behind and start importing their own stale source. Comparing against
    # what `install` would write today makes every such change self-healing, at the cost of
    # one `git config` read.
    if recorded.returncode == 0 and recorded.stdout.strip() == wanted:
        return
    try:
        read_master_key()
    except (FileNotFoundError, KeyError, ValueError):
        return  # no keypair / not issued yet — nothing to do
    console.print('[primary]Wiring the git filter and decrypting private '
                  'solutions...[/primary]')
    if run_cmdline(f'{sys.executable} -P -m solver.crypto.gitfilter install') == 0:
        resmudge_private()


@register(requires='reader', aliases=('filter',))
def git_filter(action: Literal['status', 'install'] = 'status') -> int:
    """Report or wire the transparent encryption filter for `solutions/private`.

    `status` shows the filter wiring and whether this session can unwrap the
    master key. `install` verifies master-key access first (refusing cleanly
    without it — nothing is wired), registers the clean/smudge filter in this
    clone's git config, and re-checks out `solutions/private` so existing
    ciphertext decrypts in place. The explicit form of what `git-sync` runs
    automatically after a pull that delivers key access — use it when access
    arrived some other way, e.g. right after `key-reconstruct` from shares.

    Aliased as `filter`.

    Args:
        action: 'status' reports whether the filter is configured; 'install' configures it.
            Defaults to 'status'.
    """
    if action == 'status':
        return run_cmdline(f'{sys.executable} -P -m solver.crypto.gitfilter status')
    result = run_cmdline(f'{sys.executable} -P -m solver.crypto.gitfilter install')
    if result != 0:
        return result
    # The filter is wired from here on, whatever the re-checkout below does — so both
    # tails nudge the header's chip (its private-solutions row just changed).
    result = resmudge_private()
    osc.git_changed()
    return result


@register(requires='reader', aliases=('sync',))
def git_sync(dry_run: bool = False) -> int:
    """Bring the local repository in sync with origin/master.

    On a per-user clone (branch `user/<slug>`) this is the pull flow: fetch
    origin/master and merge/rebase it into your branch — bringing in merged work
    merged work. Key material does not travel this way -- it is issued by message
    (`user-authorize` / `msg act`), and that is what wires the filter.

    Stale remote-tracking refs are pruned as part of the fetch, so a branch deleted
    when its pull request merged stops shadowing the branch you push next.

    Args:
        dry_run: Print the sync commands instead of running them. Defaults to False.
    """
    if dry_run:
        result = run_cmdline(f'{config.scripts.sync} --dry-run')
    else:
        # Fetch before deciding anything. Both questions below are about the *published*
        # tree, and a clone that has not fetched since the rotation still sees the old one —
        # it would answer "all fine" and then merge into the failure this is here to avoid.
        # `sync.sh` fetches again a moment later; one extra round-trip buys a real answer.
        read_master_key.cache_clear()
        run_cmdline('git fetch --prune origin master')
        # A clone whose HEAD predates a key rotation cannot merge — the stash resets to HEAD
        # first, HEAD's blobs no longer decrypt, and the smudge filter fails the whole sync.
        # That is exactly the state someone is in when they reach for `git-sync`, so repair it
        # here rather than hand them a traceback that names a filter they cannot fix. The
        # re-home lands them on origin/master, which is what the sync was for.
        if not private_tree_opens():
            # No edits are carried across here, and that is not an oversight: proving a private
            # file is *your* edit needs the key that opened HEAD, and by now it is gone. Diffing
            # against origin/master instead would read content you simply have not pulled yet as
            # a local change and write it back over the incoming version. `msg act` collects
            # the edits at the one moment they can be told apart, which is why this path exists
            # only for clones already wedged before it did.
            console.print('[warning]Note: uncommitted changes under solutions/private cannot be '
                          'carried across a key rotation from here, and will be replaced by the '
                          'published versions.[/warning]')
            landed = _rehome_on_origin({})
            # Non-zero when it did not land, because at shell start-up the console is quiet
            # and the exit code is the only part of a refusal that survives.
            return int(ExitCodes.EXIT_OK if landed else ExitCodes.EXIT_ERROR)
        # The other direction: this clone is coherent but holds a superseded key, so the
        # incoming blobs are the unreadable ones. Refuse before merging. Letting it run cost a
        # live collaborator a filter traceback *and* a half-applied merge that left a private
        # file deleted in their worktree — from a command they ran to get back in step.
        if hint := key_waiting_hint():
            console.print(f'[warning]{hint}[/warning]')
            return int(ExitCodes.EXIT_ERROR)
        result = run_cmdline(config.scripts.sync)
        if result == 0:
            osc.git_changed()  # the fetch moved origin/master, the merge moved the branch
    return result


@register(requires='contributor', aliases=('identity',))
def git_identity() -> int:
    """Configure your git identity and push credential from your GitHub login.

    The one-time setup before `git-push`: runs `gh auth login` when you are not yet
    signed in (interactive device flow — works in the web shell), makes gh the git
    credential helper (`gh auth setup-git`), and sets this clone's `user.name` /
    `user.email` from your GitHub profile, so your commits are authored and pushed
    as **you**, never as a service identity.

    Aliased as `identity`.
    """
    result = run_cmdline(config.scripts.configure_identity)
    if result == 0:
        osc.account_changed()  # gh sign-in flips the account page's GitHub-CLI row
    return result


# ── push / pull requests (gh) ───────────────────────────────────────────────────────────

def _open_pr_url(branch: str) -> str:
    """The URL of the open pull request for *branch*, or '' when there is none."""
    proc = run(['gh', 'pr', 'view', branch, '--json', 'url,state',
                '--jq', 'select(.state == "OPEN") | .url'],
               cwd=config.root_dir, capture_output=True, text=True)
    return proc.stdout.strip() if proc.returncode == 0 else ''


def _commits_ahead(branch: str) -> int | None:
    """How many commits `origin/<branch>` carries that origin/master does not.

    None when that cannot be determined here — no origin/master ref, or the branch
    never reached origin — in which case the caller must not infer "nothing to
    review" from a number it does not have.
    """
    proc = run(['git', 'rev-list', '--count', f'origin/master..origin/{branch}'],
               cwd=config.root_dir, capture_output=True, text=True)
    if proc.returncode != 0:
        return None
    try:
        return int(proc.stdout.strip())
    except ValueError:
        return None


def _announce_pull_request(branch: str, url: str) -> None:
    """Tell staff a pull request is waiting — the delivery half of `git-push`.

    A pull request nobody has been told about is the same dead end `user` had before the
    message layer existed: the collaborator has done everything they can, and the act that
    lands it belongs to somebody who has no reason to be looking. So the command that opens
    the request also files it, under :data:`~solver.web.msg.PR_REVIEW_SUBJECT` — the subject
    the header's chip reads to offer **merge** on that row.

    Only for a **newly opened** request. Re-pushing a branch as it grows is the normal way
    to work, and one open pull request quietly picks up the new commits; a notice per push
    would turn the queue into a changelog of somebody's afternoon.

    The branch is in the **subject**, not only the body: it is what lets the merge close
    this notice without a thread id (:func:`_dismiss_pr_notice`), and what
    :func:`merge_pr_for_branch` turns back into a number when the chip's row is pressed.

    Best-effort and silent on failure, like every other :mod:`solver.web.msg.notify` caller:
    the branch is pushed and the request is open either way, and a spool that is down must
    not fail the push that reached GitHub.
    """
    from solver.web.msg.notify import notify_staff
    # The number is the URL's last segment. The body names a command that lands *this*
    # request rather than a bare `gh-merge merge`, which would open a menu of the whole
    # queue — a notice about one branch should not make its reader pick it out again.
    number: str = url.rstrip('/').rsplit('/', 1)[-1]
    sent = notify_staff(
        f'{PR_REVIEW_SUBJECT}{branch}',
        f'{branch} has a pull request open onto master:\n\n'
        f'    {url}\n\n'
        f'To review it and land it, run:\n'
        f'    gh-merge merge {number}\n')
    if sent:
        console.print('[muted]the maintainers have been notified.[/muted]')


def _dismiss_pr_notice(branch: str) -> None:
    """Drop the notice that announced *branch*'s pull request — it has just landed.

    The closing half of :func:`_announce_pull_request`, and the reason the announcement
    named the branch in its subject: a notice that survives the act it asked for is a queue
    nobody trusts, and this one cannot be dismissed by whoever works it. The chip's row
    types a bare `gh-merge merge` (the queue that verb offers is GitHub's, not the spool's),
    so the merge holds no thread id — the subject is the only handle either side shares.

    Silent and best-effort, like the announcement: the pull request is merged either way,
    and a wedged spool must not turn a landed review into a failure. On a real dismissal
    the message chip is nudged, since the row it just removed is on screen.
    """
    if not branch:
        return
    from solver.web.msg.notify import dismiss_by_subject
    if dismiss_by_subject(f'{PR_REVIEW_SUBJECT}{branch}'):
        console.print('[muted]the review notice has been dismissed.[/muted]')
        osc.messages_changed()


def _ensure_pull_request(branch: str) -> int:
    """Open a pull request for *branch* onto master, or report the one already open.

    A pushed branch is not delivered work: landing on master needs `gh-merge`, so
    the PR is how a collaborator actually asks for their branch to land
    (scripts/git/publish.sh § publish, the same `gh pr create` shape). It is also what
    the merge gate reads — the pull request, not the branch, is what a maintainer
    approves. Idempotent — a branch already under
    review gets its URL reported, not a second PR — so re-pushing a branch as it
    grows keeps working, and the one open PR simply picks up the new commits.

    A branch level with origin/master is left alone: there is nothing to review, and
    GitHub rejects such a PR outright ("No commits between ..."). Reporting that as an
    error made a `git-push` with nothing new to say fail — the push had succeeded and
    an empty PR was never wanted, so this is a no-op, not a failure (the same reading
    as publish.sh's "Nothing to publish").
    """
    ahead: int | None = _commits_ahead(branch)
    if ahead == 0:
        console.print(f'no pull request needed: [accent]{branch}[/accent] has no commits '
                      'beyond origin/master.')
        return int(ExitCodes.EXIT_OK)
    existing: str = _open_pr_url(branch)
    if existing:
        console.print(f'pull request already open: [accent]{existing}[/accent]')
        return int(ExitCodes.EXIT_OK)
    proc = run(['gh', 'pr', 'create', '--head', branch, '--base', 'master',
                '--title', f'Publish {branch}',
                '--body', f'Publishes the work on `{branch}`.\n\n'
                          f'Opened by `git-push` on {datetime.now():%Y-%m-%d}.'],
               cwd=config.root_dir, capture_output=True, text=True)
    if proc.returncode != 0:
        detail: list[str] = (proc.stderr or proc.stdout).strip().splitlines()
        console.print('[error]error:[/error] could not open a pull request'
                      + (f': {detail[-1]}' if detail else '.'))
        console.print('your branch [accent]is[/accent] pushed — run [accent]git-identity[/accent] if gh is '
                      'not signed in, or open the PR on GitHub yourself.')
        return int(ExitCodes.EXIT_ERROR)
    url: str = proc.stdout.strip()
    console.print(f'pull request opened: [accent]{url}[/accent]')
    _announce_pull_request(branch, url)
    return int(ExitCodes.EXIT_OK)


@register(requires='contributor', quietable=True, aliases=('push',))
def git_push(force: bool = False, pr: bool = True) -> int:
    """Push the current branch to origin as yourself, then open its pull request.

    In a per-user clone the current branch is `user/<slug>`, pushed with your own
    GitHub identity — `git-identity` is the one-time setup. Landing work on master
    is a maintainer's `gh-merge`, never a direct push: pushing master requires
    the `admin` floor, and force-pushing it is always refused.

    The PR is the second half of the push: an unreviewed branch on origin is not
    work anyone has been asked for. It is skipped on master (nothing to merge into
    itself) and on a branch level with origin/master (nothing to review), and a
    branch that already has one open keeps it. Opening one also **messages the
    maintainers** that it is waiting, so the review does not depend on somebody
    thinking to look; their verb is `gh-merge merge`.

    Args:
        force: Push with `--force-with-lease` — needed after `git-sync` rebased your branch
            onto a moved origin/master. Refused on master. Defaults to False.
        pr: Open a pull request onto master after a successful push. Defaults to True;
            `--no-pr` pushes and stops there.
    """
    branch: str = _current_branch()
    if not branch or branch == 'HEAD':
        console.print('[error]error:[/error] no branch checked out.')
        return ExitCodes.EXIT_ERROR
    if branch == 'master':
        if force:
            console.print('[error]error:[/error] force-pushing master is never allowed.')
            return ExitCodes.EXIT_ERROR
        if not config.subject.has('admin'):
            console.print('[error]error:[/error] pushing master needs the [accent]admin[/accent] profile; '
                          'your work belongs on your own user/<slug> branch.')
            return ExitCodes.EXIT_ERROR
    lease: str = ' --force-with-lease' if force else ''
    result: int = run_cmdline(f'git push -u{lease} origin {branch}')
    if result == 0:
        osc.git_changed()  # origin/<branch> moved up to HEAD: the chip's ahead count
    if result != 0 or not pr or branch == 'master':
        return result
    return _ensure_pull_request(branch)


#: What a collaborator's pull request may touch — the merge gate's allowlist, and the one
#: rule `gh-merge` applies: solutions (progress file and tag legs included), the guides,
#: the topic articles, and the specific files the `update` target names. Read by
#: :func:`_in_scope`, so a `dir/` entry is a prefix and a lookalike sibling
#: (`solutions-of-mine/`) does not pass.
#:
#: It is exactly the union of :data:`TARGET_PATHS` — **a pull request may carry whatever
#: `git-commit` could have staged, and nothing else.** That equivalence is the gate: a
#: branch of solutions, articles and a regeneration is one review a maintainer can do,
#: because every file in it came from a commit verb they know the shape of. A branch that
#: also edits the framework, the scripts or the keys is asking for something else
#: entirely — merge that on GitHub, as an admin who has read it.
#:
#: There is deliberately **no one-tree rule** and no per-body-of-work gate. A pull request
#: may carry several commits spanning several targets, so splitting the queue by tree only
#: refused branches that were honest work; what the review needs to know is that nothing
#: outside the allowlist rode along, which is what this checks.
PR_SCOPE: tuple[str, ...] = ('solutions/', 'docs/', 'topics/') + TARGET_PATHS['update']


def _pr_files(number: int) -> list[str] | None:
    """Every path pull request *number* touches, or None when that cannot be read.

    None is NOT "no files": a `gh` that is unauthenticated or offline, and a pull
    request that does not exist, all fail here. The merge gate must refuse on a file
    list it could not read rather than read an empty one as "touches nothing outside
    the scope" and merge.
    """
    proc = run(['gh', 'pr', 'view', str(number), '--json', 'files', '--jq', '.files[].path'],
               cwd=config.root_dir, capture_output=True, text=True)
    if proc.returncode != 0:
        return None
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def _open_prs() -> list[dict[str, object]] | None:
    """The open pull requests as `{number, title, branch}` records, or None on failure.

    None is NOT "no open PRs": an unauthenticated or offline `gh` fails here, and the
    caller must not read that as an empty queue. `gh pr list` defaults to open PRs; the
    JSON fields are the three a reviewer needs to decide (number, title, branch).
    """
    proc = run(['gh', 'pr', 'list', '--json', 'number,title,headRefName'],
               cwd=config.root_dir, capture_output=True, text=True)
    if proc.returncode != 0:
        return None
    try:
        data = json.loads(proc.stdout or '[]')
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, list) else None


def _open_queue() -> list[dict[str, object]] | None:
    """The open pull requests, reporting the one failure that stops every merge path.

    Both ways in — a number typed at `gh-merge merge`, and a branch named by a review
    notice — need the same read and fail it the same way, so the diagnostic lives here
    rather than being written twice and drifting.
    """
    prs: list[dict[str, object]] | None = _open_prs()
    if prs is None:
        console.print('[error]error:[/error] cannot read the open pull requests — is [accent]gh[/accent] '
                      'signed in ([accent]git-identity[/accent])?')
    return prs


def merge_pr_for_branch(branch: str) -> int:
    """Merge the open pull request for *branch* — the act behind a review notice.

    `msg act` on a :data:`~solver.web.msg.PR_REVIEW_SUBJECT` message must land **that**
    request, and the subject names a branch where the gate needs a number. The open queue
    is what turns one into the other, and it is the read the merge wants anyway.

    It used to call `gh-merge merge` with nothing at all, which was right only while that
    verb walked the whole queue: with the queue offered as a menu, pressing **merge** on one
    notice would ask the reader to pick a request out of a list they had just been told the
    answer to — and let them pick a different one. A notice about one branch lands that
    branch.

    No open request for this branch is worth saying rather than falling back to a menu: the
    notice has outlived what it asked for (already merged, or closed), and that is the fact
    the reader needs.
    """
    if not branch:
        console.print('[error]error:[/error] this notice names no branch — run '
                      '[accent]gh-merge list[/accent] and merge by number.')
        return ExitCodes.EXIT_ERROR
    prs = _open_queue()
    if prs is None:
        return ExitCodes.EXIT_ERROR
    number = next((pr.get('number') for pr in prs
                   if str(pr.get('headRefName', '')) == branch), None)
    if not isinstance(number, int):
        console.print(f'[error]error:[/error] no open pull request for [accent]{branch}[/accent] — '
                      'it may already have been merged or closed. Run [accent]gh-merge list[/accent] '
                      'to see what is waiting.')
        return ExitCodes.EXIT_ERROR
    return _merge_pr(number, branch=branch)


def _merge_pr(number: int, *, branch: str = '') -> int:
    """Rebase-merge pull request *number* onto master, refusing anything beyond :data:`PR_SCOPE`.

    Rebase, not squash: each of the branch's commits is replayed onto master (with fresh
    SHAs), so a review of several commits lands as several commits rather than one folded
    checkpoint — master's history stays linear, and the individual commits survive.

    One gate, one question: **is every file in the allowlist?** A pull request may carry
    as many commits, and span as many of `git-commit`'s targets, as the work needed — what
    makes this a maintainer's command rather than an admin's is that nothing outside
    :data:`PR_SCOPE` rode along. On a clean merge the header chip is nudged
    (:func:`osc.git_changed`), since master moved.

    *branch* is the request's head ref, carried only so a landed merge can close the
    notice that asked for it (:func:`_dismiss_pr_notice`). Optional because the merge is
    complete without it: the spool is a nudge on top, never part of the gate.
    """
    files: list[str] | None = _pr_files(number)
    if files is None:
        console.print(f'[error]error:[/error] cannot read the files of pull request [accent]#{number}'
                      '[/accent] — does it exist, and is [accent]gh[/accent] signed in '
                      '([accent]git-identity[/accent])?')
        return ExitCodes.EXIT_ERROR
    if not files:
        console.print(f'[error]error:[/error] pull request [accent]#{number}[/accent] touches no files.')
        return ExitCodes.EXIT_ERROR
    outside: list[str] = [path for path in files if not _in_scope(path, PR_SCOPE)]
    if outside:
        console.print(f'[error]error:[/error] pull request [accent]#{number}[/accent] touches '
                      f'{len(outside)} file(s) outside [accent]{" / ".join(PR_SCOPE)}[/accent]:')
        for path in outside[:10]:
            console.print(f'  !! {path}')
        if len(outside) > 10:
            console.print(f'  … and {len(outside) - 10} more')
        console.print('this is not a content review — merge it on GitHub if it is genuinely wanted.')
        return ExitCodes.EXIT_ERROR
    trees: list[str] = sorted({entry for path in files for entry in PR_SCOPE if _in_scope(path, (entry,))})
    console.print(f'pull request [accent]#{number}[/accent]: {len(files)} file(s), all under '
                  f'[accent]{" / ".join(trees)}[/accent] — merging.')
    # --admin: land it immediately with administrator privileges. master's base-branch
    # policy prohibits a plain merge (that policy is what gates other collaborators);
    # the owner running this review has the bypass, and without --admin `gh pr merge`
    # just refuses with "the base branch policy prohibits the merge".
    result: int = run_cmdline(f'gh pr merge {number} --rebase --admin')
    if result != 0:
        return result
    # Before the sync, and independent of it: the review is what the notice asked for, and
    # it is done. A sync that then fails (a conflicted rebase, say) leaves work to do on
    # this clone — not a pull request still waiting for a reviewer.
    _dismiss_pr_notice(branch)
    return git_sync()


def _is_merge(bound: dict[str, Any]) -> bool:
    """Whether the verb is the one that needs a pull request named — only `merge` does."""
    return bound.get('action') == 'merge'


def _open_pr_choices(_ctx: Any, _bound: dict[str, Any]) -> list[Choice]:
    """The open pull requests as menu options, so the number never has to be typed out.

    The same read `gh-merge list` prints, offered as a chooser: each row is the number
    (the value bound to `pr_number`), the title, and the branch it would land. An
    unreadable queue comes back empty rather than raising — the dialogue says there is
    nothing to choose, and the caller's own `_open_prs` read reports *why* on the path
    that matters.
    """
    return [Choice(str(number), f'#{number}  {pr.get("title", "")}',
                   str(pr.get('headRefName', '')))
            for pr in _open_prs() or []
            if isinstance(number := pr.get('number'), int)]


@register(requires='maintainer', quietable=True, aliases=('merge',))
def gh_merge(action: Literal['list', 'merge'] = 'list',
             pr_number: Annotated[int, Ask('Which pull request?', choices=_open_pr_choices,
                                           when=_is_merge, empty='no open pull requests')] = 0,
             ) -> int:
    """List the open pull requests, or rebase-merge one onto master.

    `list` (the default) shows what is waiting: number, title, branch. `merge` lands one
    of them, named by number and offered as a menu when you leave it out. Merging is how a
    collaborator's `user/<slug>` branch reaches master, each of its commits replayed onto
    the tip; their next `git-sync` then rebases those already-applied commits away and
    prunes the merged branch. It also **dismisses the notice** `git-push` filed for that
    branch — the message asked for this review, and it is done.

    Every file in the pull request must sit inside the allowlist: `solutions/`, `docs/`,
    `topics/`, and the specific files the `update` target names — which is exactly what
    `git-commit` can stage. One file outside it refuses the whole request. That is the
    gate, and the only one: a request may carry as many commits, across as many targets,
    as the work needed. What makes this a maintainer's command rather than an admin's is
    that everything in it came from a commit verb they know the shape of; a branch that
    also edits the framework, the scripts, or the keys is asking for something else
    entirely, and belongs on GitHub in front of an admin who has read it.

    Aliased as `merge`.

    Args:
        action: 'list' shows the open queue; 'merge' lands one request. Defaults to 'list'.
        pr_number: [asked] Which pull request to merge, by number. Offered as a menu of the
            open requests when omitted, so the number never has to be typed out; only ever
            required for `merge`.
    """
    if action == 'list':
        return run_cmdline('gh pr list')
    # Read the queue even when the number came in on the command line: it says whether the
    # request is open (a merged or invented number would otherwise reach `gh` as a refusal
    # nobody can act on), and it carries the head ref that closes the review notice.
    prs = _open_queue()
    if prs is None:
        return ExitCodes.EXIT_ERROR
    if not pr_number:
        # Only reachable non-interactively: at the prompt the menu above collects it first.
        if not prs:
            console.print('no open pull requests — nothing to merge.')
            return ExitCodes.EXIT_OK
        console.print('[error]error:[/error] which pull request? pass '
                      '[accent]gh-merge merge <number>[/accent] — [accent]gh-merge list[/accent] '
                      'shows the queue.')
        return ExitCodes.EXIT_USAGE
    record = next((pr for pr in prs if pr.get('number') == pr_number), None)
    if record is None:
        console.print(f'[error]error:[/error] no open pull request [accent]#{pr_number}[/accent] — '
                      'run [accent]gh-merge list[/accent] to see the queue.')
        return ExitCodes.EXIT_ERROR
    # The head ref comes from the same read that offered the row, so the notice `git-push`
    # filed under this branch is closed by the merge that answers it.
    return _merge_pr(pr_number, branch=str(record.get('headRefName', '')))


# ── hooks / audit ───────────────────────────────────────────────────────────────────────

@register(requires='contributor', aliases=('hooks',), quietable=True)
def git_hooks() -> int:
    """Run the git pre-commit and (simulated) pre-push checks on demand.

    Runs the same checks the git hooks run — the pre-commit hook (whitespace
    fixes, flake8, mypy) and a simulation of the pre-push hook — so you can
    verify your changes will pass before committing or pushing. Reports the
    combined pass/fail in the exit code.

    Aliased as `hooks`.
    """
    console.print('[primary]Running pre-commit hooks...[/primary]')
    run_cmdline(config.root_dir.joinpath('.git/hooks/pre-commit').as_posix())
    console.print('[primary]Running simulated pre-push hooks...[/primary]')
    cmd_line = ('echo "refs/heads/master $(git rev-parse HEAD) refs/heads/master $(git rev-parse origin/master)" | '
                f'{config.root_dir.joinpath(".git/hooks/pre-push").as_posix()}')
    result = run_cmdline(cmd_line)
    return result


@register(requires='contributor', aliases=('audit',), quietable=True)
def git_audit(details: bool = False) -> int:
    """Audit what git actually stores, across the whole tracked tree.

    Two checks, each reading every tracked blob straight from the object store (so
    no smudge filter runs): every file under `solutions/private` is stored as
    ciphertext, and no file anywhere is a compiled binary. Both run even when the
    first fails; a non-zero exit means one of them found something.

    This is the periodic full sweep, and it takes ~25s. The git hooks run the same
    two checks scoped to the blobs at hand — `git-hooks` (pre-commit) audits what
    you staged, pre-push audits what the push would add — so committing and pushing
    stay fast. The cost of that scoping is that neither hook re-examines history
    already on origin; this is the command that does.

    Aliased as `audit`.

    Args:
        details: List every file audited. Defaults to False, which reports counts only;
            offenders are listed by path either way.
    """
    # Name the interpreter rather than let the script resolve `python` off PATH: the
    # web shell inherits the euler-user unit's PATH, which has no venv on it (the unit
    # execs the venv python by absolute path), and this host has no /usr/bin/python at
    # all. `sys.executable` is the venv either way — the same idiom as `git-filter`.
    flag: str = '' if details else ' --summary'
    return run_cmdline(f'PYTHON={sys.executable} {config.scripts.audit}{flag}')

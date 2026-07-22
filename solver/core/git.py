#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Git and GitHub (gh) commands and helpers — the repository workflow.

Per-user native git (docs/web-server-guide.md § Git): a collaborator's shell runs in
**their own clone** on branch ``user/<slug>`` as their own uid, so git needs no
broker — the read verbs (`git-status`, `git-sync`) are ``reader``-floor and the
write verbs (`git-commit`, `git-push`, `git-hooks`) plus the tree audit
(`git-audit`) are ``contributor``-floor; the blast radius is their own branch.
``master`` stays gated: `gh-pr merge` (``maintainer``) is the one gate through which
a ``user/<slug>`` branch lands on master, and it opens only for a pull request that sits
wholly inside one of the content trees a collaborator authors — ``solutions/`` **or**
``topics/``, never both (:data:`PR_SCOPE`).
"""
from __future__ import annotations

__all__ = ['get_gh_user_email', 'get_repo_owner_email', 'git_commit', 'git_commit_amend',
           'git_publish', 'git_status', 'git_filter', 'git_sync', 'git_identity', 'git_push',
           'gh_pr', 'git_hooks', 'git_audit']

import json
import sys
from datetime import datetime
from functools import lru_cache
from subprocess import run
from typing import Literal

from solver.config import ExitCodes, config
from solver.core import osc
from solver.core.problems import Problem
from solver.crypto.ciphers import read_master_key
from solver.crypto.config import config as crypto_config
from solver.shell import console, register
from solver.utils.shell_utils import run_cmdline, run_command


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


# ── commit / amend ──────────────────────────────────────────────────────────────────────

def _current_branch() -> str:
    """The checked-out branch name ('' when detached or not a repo)."""
    proc = run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
               cwd=config.root_dir, capture_output=True, text=True)
    return proc.stdout.strip() if proc.returncode == 0 else ''


def _commit_paths(problem: Problem) -> list[str]:
    """The paths a commit stages for *problem* — its directory and the progress file."""
    return [problem.solution_dir.as_posix(), config.static_file_problems.as_posix()]


@register(requires='contributor',
          help_text="Commit a problem's solution directory and progress, optionally resetting to origin/master.",
          aliases=('commit',), quietable=True, )
def git_commit(problem: Problem, message: str = '', *, reset: bool = False) -> int:
    """Stage and commit the problem's solution directory.

    Adds everything under `problem.solution_dir`, plus `solutions/problems.json`
        (the progress file `mark` rewrites), and commits just those
        — the routine "save my progress" step.

    Args:
        problem:        The problem to commit.
        message:        The commit message. When empty (the default) and `reset` is not
                        set, folds into the last unpushed commit if there is one to amend
                        (see `git-commit-amend`); otherwise commits fresh under the
                        default message "solution for pNNNN".
        reset:          When True, first soft-reset to `origin/master` so the new commit
                        squashes all local commits into a single checkpoint (working
                        tree untouched). Defaults to False. Suppresses the empty-message
                        amend, since squashing to one checkpoint is the opposite intent.
    Aliased as `commit`.
    """
    # Empty message with no reset prefers folding into HEAD — but only when the loud
    # `git-commit-amend` would actually amend; `_can_amend` decides that quietly so its
    # refusal diagnostics never surface on a path that then commits fresh. `reset` opts
    # out entirely: it squashes local commits into one checkpoint, not into HEAD.
    if not message and not reset and _can_amend(problem):
        return git_commit_amend(problem)
    if not message:
        message = f'solution for p{problem.number:04d}'
    cmdline: list[str] = ['git', 'reset', '--soft', 'origin/master', '&&'] if reset else []
    cmdline += ['git', 'add', '-A', *_commit_paths(problem), '&&']
    cmdline += ['git', 'commit', '--message', f'"{message}"']
    result = run_cmdline(' '.join(cmdline))
    if result == 0:
        osc.git_changed()
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


def _can_amend(problem: Problem) -> bool:
    """Whether `git-commit-amend` would actually amend *problem* — decided quietly.

    True only when all three of amend's preconditions hold: there is a HEAD to amend,
    it is unpushed (so no force-push would be needed), and this problem's paths are
    dirty. `git_commit_amend` reports *why* each of these fails; this answers only
    whether an empty-message `git-commit` should fold into HEAD, without printing, so
    the loud command is called only on the path where it succeeds.
    """
    if run(['git', 'rev-parse', '--verify', '--quiet', 'HEAD'],
           cwd=config.root_dir, capture_output=True).returncode != 0:
        return False
    if _remotes_containing_head() != []:  # None (undecidable) or non-empty (pushed) → do not amend
        return False
    dirty: str = run(['git', 'status', '--porcelain', '--', *_commit_paths(problem)],
                     cwd=config.root_dir, capture_output=True, text=True).stdout.strip()
    return bool(dirty)


@register(requires='contributor', quietable=True,
          help_text="Amend the last unpushed commit with a problem's current changes.",
          aliases=('amend',), )
def git_commit_amend(problem: Problem) -> int:
    """Fold this problem's current changes into the last commit, message unchanged.

    The "I forgot something" step after `git-commit`: stages everything under
        `problem.solution_dir` plus `solutions/problems.json` and amends HEAD with
        `--no-edit`, so the checkpoint absorbs the fix instead of growing a
        "fix typo" commit behind it.

    Refused once HEAD is on origin — amending rewrites the commit, and a rewritten
        commit that is already pushed only lands again through a force-push, so
        `git-commit` is the honest step there. A no-op, not a failure, when nothing
        under those paths has changed.

    Args:
        problem:        The problem whose changes are folded into HEAD.

    Aliased as `amend`.
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
                      'amending it would need a force-push — use [accent]git-commit[/accent] instead.')
        return ExitCodes.EXIT_ERROR
    paths: list[str] = _commit_paths(problem)
    dirty: str = run(['git', 'status', '--porcelain', '--', *paths],
                     cwd=config.root_dir, capture_output=True, text=True).stdout.strip()
    if not dirty:
        console.print(f'nothing to amend: [accent]p{problem.number:04d}[/accent] and the progress file '
                      'are unchanged.')
        return int(ExitCodes.EXIT_OK)
    result = run_cmdline(f'git add -A {" ".join(paths)} && git commit --amend --no-edit')
    if result == 0:
        osc.git_changed()
    return result


# ── publish / status / sync / filter / identity ─────────────────────────────────────────

@register(
    requires='admin',
    help_text='Push targets (keys|scripts|[accent]solutions[/accent]|solver) to remote.',
    aliases=('publish',),
    quietable=True,
)
def git_publish(*targets: Literal['keys', 'scripts', 'solutions', 'solver'],
                dry_run: bool = False) -> int:
    """Publish changed files for named targets to the remote repository.

    Args:
        targets: Scopes of files to publish — one or more of 'keys', 'scripts', 'solutions', or 'solver'.
                 Defaults to 'solutions'.
        dry_run: Print the push and pull-request commands instead of running them.  Defaults to False.

    Raises:
        ValueError: If any target is not one of the accepted values.
    """
    if not targets:
        targets = ('solutions',)
    if not all(target in ['keys', 'scripts', 'solutions', 'solver'] for target in targets):
        raise ValueError(f'Invalid targets: {", ".join(targets)}')
    if dry_run:
        result = run_cmdline(f'{config.scripts.publish} --dry-run {" ".join(targets)}')
    else:
        result = run_cmdline(f'{config.scripts.publish} {" ".join(targets)}')
    return result


@register(requires='reader',
          help_text='Display sync state between local and origin/master.', aliases=('status',), )
def git_status(details: bool = False) -> int:
    """Display the sync state between the local branch and origin/master.

    Args:
        details:    When True, lists every differing file and uncommitted change.
                    When False (default), shows file counts only.
    """
    if details:
        result = run_cmdline(config.scripts.status)
    else:
        result = run_cmdline(f'{config.scripts.status} --summary')
    return result


def _enc_key_pull_flow() -> None:
    """The self-service tail of a sync: wire the git filter once key access exists.

    A provisioned clone starts filter-UNWIRED with ``solutions/private/**`` as
    ciphertext. When a pull delivers a ``keys/enc-key.json`` that wraps the master key to
    this user's public key (an admin ran ``user-authorize`` and pushed), wire the
    clean/smudge filter and re-checkout the private tree — ciphertext becomes plaintext
    in place. A silent no-op while the filter is already wired or the user is not (yet)
    key-authorized, so every sync may call it.
    """
    name: str = crypto_config['filter_name']
    wired: bool = run(['git', 'config', '--local', '--get', f'filter.{name}.process'],
                      cwd=config.root_dir, capture_output=True).returncode == 0
    if wired:
        return
    read_master_key.cache_clear()  # this very pull may have delivered access
    try:
        read_master_key()
    except (FileNotFoundError, KeyError, ValueError):
        return  # no keypair / not authorized — nothing to do
    console.print('[primary]Master-key access detected — wiring the git filter and '
                  'decrypting private solutions...[/primary]')
    if run_cmdline(f'{sys.executable} -m solver.crypto.gitfilter install') == 0:
        run_cmdline('git ls-files -z -- solutions/private | xargs -0 -r rm -f -- '
                    '&& git checkout -- solutions/private')


@register(requires='reader', aliases=('filter',),
          help_text='Wire the git encryption filter: [accent.dim]status[/accent.dim] | install.')
def git_filter(action: Literal['status', 'install'] = 'status') -> int:
    """Report or wire the transparent encryption filter for `solutions/private`.

    `status` shows the filter wiring and whether this session can unwrap the
    master key. `install` verifies master-key access first (refusing cleanly
    without it — nothing is wired), registers the clean/smudge filter in this
    clone's git config, and re-checks out `solutions/private` so existing
    ciphertext decrypts in place. The explicit form of what `git-sync` runs
    automatically after a pull that delivers key access — use it when access
    arrived some other way, e.g. right after `key-reconstruct` from shares.

    Args:
        action: 'status' (default) or 'install'.

    Aliased as `filter`.
    """
    if action == 'status':
        return run_cmdline(f'{sys.executable} -m solver.crypto.gitfilter status')
    result = run_cmdline(f'{sys.executable} -m solver.crypto.gitfilter install')
    if result != 0:
        return result
    # The filter is wired from here on, whatever the re-checkout below does — so both
    # tails nudge the header's chip (its private-solutions row just changed).
    # Re-smudge: existing ciphertext in the worktree only decrypts on a fresh
    # checkout. Genuine local edits must not be clobbered — but a freshly wired
    # clone is NOT dirty (clean() passes ciphertext through, matching the stored
    # blob), so the guard only trips on real plaintext changes.
    dirty: str = run(['git', 'status', '--porcelain', '--', 'solutions/private'],
                     cwd=config.root_dir, capture_output=True, text=True).stdout.strip()
    if dirty:
        console.print('[warning]solutions/private has local changes — skipping the re-checkout; '
                      'commit or stash, then run [accent]git-filter install[/accent] again.[/warning]')
        osc.git_changed()
        return int(ExitCodes.EXIT_OK)
    console.print('[primary]Decrypting private solutions in place...[/primary]')
    result = run_cmdline('git ls-files -z -- solutions/private | xargs -0 -r rm -f -- '
                         '&& git checkout -- solutions/private')
    osc.git_changed()
    return result


@register(requires='reader',
          help_text='Bring the local repository in sync with origin/master.', aliases=('sync',), )
def git_sync(dry_run: bool = False) -> int:
    """Bring the local repository in sync with origin/master.

    On a per-user clone (branch `user/<slug>`) this is the pull flow: fetch
    origin/master and merge/rebase it into your branch — bringing in merged work
    and, notably, `keys/enc-key.json`. When that pull first delivers master-key
    access for your key, the git filter is wired automatically and the private
    solutions decrypt in place.

    Stale remote-tracking refs are pruned as part of the fetch, so a branch deleted
    when its pull request merged stops shadowing the branch you push next.

    Args:
        dry_run: Print the sync commands instead of running them. Defaults to False.
    """
    if dry_run:
        result = run_cmdline(f'{config.scripts.sync} --dry-run')
    else:
        result = run_cmdline(config.scripts.sync)
        if result == 0:
            _enc_key_pull_flow()
            # The fetch moved origin/master, the merge moved the branch, and the flow
            # above may have wired the filter: everything the chip shows.
            osc.git_changed()
    return result


@register(requires='contributor',
          help_text='Sign in to GitHub (gh) and set this clone\'s git identity from it.',
          aliases=('identity',), )
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
    """How many commits ``origin/<branch>`` carries that origin/master does not.

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


def _ensure_pull_request(branch: str) -> int:
    """Open a pull request for *branch* onto master, or report the one already open.

    A pushed branch is not delivered work: landing on master needs `gh-pr merge`, so
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
    console.print(f'pull request opened: [accent]{proc.stdout.strip()}[/accent]')
    return int(ExitCodes.EXIT_OK)


@register(requires='contributor', quietable=True,
          help_text='Push the current branch to origin and open a pull request onto master.',
          aliases=('push',), )
def git_push(force: bool = False, pr: bool = True) -> int:
    """Push the current branch to origin as yourself, then open its pull request.

    In a per-user clone the current branch is `user/<slug>`, pushed with your own
    GitHub identity — `git-identity` is the one-time setup. Landing work on master
    is a maintainer's `gh-pr merge`, never a direct push: pushing master requires
    the `admin` floor, and force-pushing it is always refused.

    The PR is the second half of the push: an unreviewed branch on origin is not
    work anyone has been asked for. It is skipped on master (nothing to merge into
    itself) and on a branch level with origin/master (nothing to review), and a
    branch that already has one open keeps it.

    Args:
        force: Push with `--force-with-lease` — needed after `git-sync` rebased your
               branch onto a moved origin/master. Refused on master.
        pr:    Open a pull request onto master after a successful push. Defaults to
               True; `--no-pr` pushes and stops there.
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


#: The content trees a collaborator's pull request may touch: solutions (plus the
#: progress file) and topic articles. Framework code, scripts, keys and docs reach master
#: another way, and `gh-pr merge` is not the review for those. Prefixes, so a lookalike
#: sibling (`solutions-of-mine/`) does not pass.
#:
#: **One tree per pull request.** A review is of one kind of work — solving a problem or
#: writing an article — and the two carry different risks: solutions bring encrypted
#: files and the progress file, articles bring prose and the reconciled tag graph. A
#: branch that mixes them is two reviews wearing one hat, so the gate refuses it and asks
#: for two pull requests.
PR_SCOPE: tuple[str, ...] = ('solutions/', 'topics/')


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
    """The open pull requests as ``{number, title, branch}`` records, or None on failure.

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


def _merge_pr(number: int) -> int:
    """Squash-merge pull request *number* onto master, refusing anything beyond :data:`PR_SCOPE`.

    The gate that makes this a maintainer's command rather than an admin's: merging a
    branch that carries solutions or topic articles is reviewing content, but a branch
    that also edits the framework, the scripts, or the keys is asking for something else
    entirely — merge those on GitHub, as an admin who has read them. The files must sit
    in **one** of the trees, never both (:data:`PR_SCOPE`). On a clean merge the header
    chip is nudged (:func:`osc.git_changed`), since master moved.
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
    outside: list[str] = [path for path in files if not path.startswith(PR_SCOPE)]
    if outside:
        console.print(f'[error]error:[/error] pull request [accent]#{number}[/accent] touches '
                      f'{len(outside)} file(s) outside [accent]{" / ".join(PR_SCOPE)}[/accent]:')
        for path in outside[:10]:
            console.print(f'  !! {path}')
        if len(outside) > 10:
            console.print(f'  … and {len(outside) - 10} more')
        console.print('this is not a content review — merge it on GitHub if it is genuinely wanted.')
        return ExitCodes.EXIT_ERROR
    trees: list[str] = sorted({prefix for path in files for prefix in PR_SCOPE if path.startswith(prefix)})
    if len(trees) > 1:
        console.print(f'[error]error:[/error] pull request [accent]#{number}[/accent] spans '
                      f'[accent]{" and ".join(trees)}[/accent] — one tree per review.')
        console.print('split it into a pull request per tree, then merge them separately.')
        return ExitCodes.EXIT_ERROR
    console.print(f'pull request [accent]#{number}[/accent]: {len(files)} file(s), all under '
                  f'[accent]{trees[0]}[/accent] — merging.')
    # --admin: land it immediately with administrator privileges. master's base-branch
    # policy prohibits a plain merge (that policy is what gates other collaborators);
    # the owner running this review has the bypass, and without --admin `gh pr merge`
    # just refuses with "the base branch policy prohibits the merge".
    result: int = run_cmdline(f'gh pr merge {number} --squash --admin')
    if result == 0:
        osc.git_changed()  # master moved: the chip's ahead/behind counts changed
    return result


def _merge_walk() -> int:
    """Walk the open pull requests interactively — merge / skip / quit each.

    The interactive counterpart of `users process-requests`: read the open PRs once,
    then per request show its number, title and branch and offer **merge** (the
    `solutions/`-gated squash), **skip** (leave it open), or **quit**. Merging is
    :func:`_merge_pr`, so the same file gate and the same git-changed nudge apply as a
    numbered merge once did.
    """
    prs: list[dict[str, object]] | None = _open_prs()
    if prs is None:
        console.print('[error]error:[/error] cannot read the open pull requests — is [accent]gh[/accent] '
                      'signed in ([accent]git-identity[/accent])?')
        return ExitCodes.EXIT_ERROR
    if not prs:
        console.print('[muted]no open pull requests[/muted]')
        return int(ExitCodes.EXIT_OK)
    console.print(f'[accent]{len(prs)}[/accent] open pull request(s) — per request: '
                  '[accent]m[/accent]erge · [accent]s[/accent]kip · [accent]q[/accent]uit')
    for pr in prs:
        number = pr.get('number')
        if not isinstance(number, int):
            continue
        title = str(pr.get('title', ''))
        branch = str(pr.get('headRefName', ''))
        console.print()
        console.print(f'  [accent]#{number}[/accent]  {title}  [muted]{branch}[/muted]')
        choice = console.input('  [accent]m/s/q[/accent] > ').strip().lower()[:1]
        if choice == 'q':
            break
        if choice != 'm':
            console.print('  [muted]skipped[/muted]')
            continue
        _merge_pr(number)
    return int(ExitCodes.EXIT_OK)


@register(requires='maintainer', quietable=True,
          help_text='Pull requests: [accent.dim]list[/accent.dim] | merge (walk the queue).',
          aliases=('pr',), )
def gh_pr(action: Literal['list', 'merge'] = 'list') -> int:
    """List the open pull requests, or walk them one at a time to squash-merge.

    `list` (the default) shows what is waiting: number, title, branch. `merge` walks
    the open pull requests interactively — per request **merge** (squash onto master),
    **skip**, or **quit** — the same shape as `users process-requests`. Merging one is
    how a collaborator's `user/<slug>` branch lands on master; their next `git-sync`
    then rebases the squashed commit away and prunes the merged branch.

    A pull request must sit wholly inside `solutions/` **or** wholly inside `topics/` —
    anything else is refused, and a branch spanning both is asked to become two pull
    requests. That gate is what makes this a maintainer's command rather than an admin's:
    merging a branch that carries solutions or topic articles is reviewing content,
    but a branch that also edits the framework, the scripts, or the keys is asking for
    something else entirely. Merge those on GitHub, as an admin who has read them.

    Args:
        action: 'list' (default) or 'merge' (walk the open queue interactively).

    Aliased as `pr`.
    """
    if action == 'list':
        return run_cmdline('gh pr list')
    return _merge_walk()


# ── hooks / audit ───────────────────────────────────────────────────────────────────────

@register(
    requires='contributor',
    help_text='Run pre-commit hook and simulated pre-push hook.',
    aliases=('hooks',),
    quietable=True,
)
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


@register(
    requires='contributor',
    help_text='Audit the whole tracked tree: private encrypted, no compiled binaries.',
    aliases=('audit',),
    quietable=True,
)
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

    Args:
        details: When True, lists every file audited. When False (default), reports
                 counts only. Offenders are listed by path either way.

    Aliased as `audit`.
    """
    # Name the interpreter rather than let the script resolve `python` off PATH: the
    # web shell inherits the euler-user unit's PATH, which has no venv on it (the unit
    # execs the venv python by absolute path), and this host has no /usr/bin/python at
    # all. `sys.executable` is the venv either way — the same idiom as `git-filter`.
    flag: str = '' if details else ' --summary'
    return run_cmdline(f'PYTHON={sys.executable} {config.scripts.audit}{flag}')

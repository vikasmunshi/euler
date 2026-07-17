#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The header chip's git state: two reads of this user's clone.

The chip in the header (``_git.html``) answers three questions — what branch am I
on, how far is it from where it should be, and can I read the private solutions.

Two commands, because they answer two different questions:

- ``git status --porcelain=v2 --branch`` — the branch and a line per changed file.
- ``git rev-list --left-right --count origin/master...HEAD`` — the divergence.

The second is not redundant with the first's ``# branch.ab``. That field counts
against the branch's *tracking* branch, which for a collaborator is
``origin/user/<slug>`` — it answers "have I pushed?". The question this workspace
actually turns on is "how far am I from **master**?", because master is where work
lands and ``git-sync`` is what closes the gap. So the chip measures what
``scripts/git/status.sh`` measures, against the same ref: **origin/master, always**.
``rev-list`` walks refs only — no worktree scan, no filter — so the second read is
cheap beside the first.

**Local refs only.** Neither command touches the network, so the divergence is
measured against ``origin/master`` *as this clone last fetched it* — the freshness
of a ``git-sync``, not of the remote (``status.sh`` fetches first; a page render must
not). That is the honest reading for a status light: it reports the clone, and the
clone is what the user's commands act on. The panel says so in as many words.

**No optional locks.** ``git status`` normally takes ``.git/index.lock`` to write
back the refreshed stat cache. This module is a *reader* on a page render, and the
user is typing real git commands into their terminal one pane away: a status read
that grabs the index lock can make their ``git-commit`` fail, and several concurrent
renders can collide with each other. ``--no-optional-locks`` is git's own answer for
status displays — it costs a little repeated hashing and takes no lock.

**Who runs this.** The per-user service (:mod:`solver.web.user`) *is* the
collaborator's uid and owns their clone, so the read succeeds there. The shared
content service (:mod:`solver.web.site`) runs as a uid with no access to ``.git``
(``SiteConfig.github_url`` documents the same boundary) — there :func:`read` returns
``None`` and the header simply shows no chip, rather than an error or a guess.

**When the vault is locked.** With the filter wired, git hashes a changed file
through the clean filter, which needs the master key. A locked vault therefore turns
a status read into a failure — as does any other git trouble. Every one of those is
the same answer here: :attr:`GitState.unknown`. The chip says it does not know;
it never says "clean" on data it could not read.
"""
from __future__ import annotations

__all__ = ['GitState', 'filter_wired', 'read']

import asyncio
import logging
from dataclasses import dataclass, replace
from pathlib import Path

from solver.crypto.config import config as crypto_config

log = logging.getLogger('euler-content')

#: Ceiling on each read. They are local commands, but they run on the event loop's
#: watch and a wedged git (a locked vault, a stale index.lock) must not hold a page
#: render. Overrunning it reads as `unknown`, like any other failure.
_TIMEOUT: float = 5.0

#: The ref the chip measures against — **always**, whatever the branch's own tracking
#: branch says. Master is where work lands and `git-sync` is what closes the gap, so
#: "how far am I from master?" is the question the chip exists to answer. This is the
#: ref `scripts/git/status.sh` uses, and the two must not drift.
_UPSTREAM: str = 'origin/master'


@dataclass(frozen=True, slots=True)
class GitState:
    """One clone's state, as the header chip shows it.

    ``unknown`` is the honest zero value: the clone is there but git would not answer
    (a locked vault, a timeout, a detached HEAD with no upstream). Every field below
    it is then meaningless and the template shows none of them.
    """

    #: Current branch, e.g. ``user/vikas``. Empty on a detached HEAD.
    branch: str = ''
    #: The ref the divergence is measured against — ``origin/master``, always (§ module
    #: docstring). Empty when this clone has no such ref, which is the one case the
    #: counts below mean nothing and the chip shows neither.
    upstream: str = ''
    #: Commits on this branch that ``origin/master`` does not have (as of the last fetch).
    ahead: int = 0
    #: Commits on ``origin/master`` that this branch does not have (as of the last fetch).
    behind: int = 0
    #: Tracked files changed in the worktree but not staged.
    modified: int = 0
    #: Files staged for the next commit.
    staged: int = 0
    #: Files git is not tracking (excluding ignored ones).
    untracked: int = 0
    #: True when the private solutions are readable here: the clean/smudge filter is
    #: wired in this clone (:mod:`solver.crypto.gitfilter`).
    filter_wired: bool = False
    #: True when the read failed — the chip renders "state not read", not "clean".
    unknown: bool = False

    @property
    def dirty(self) -> bool:
        """Whether the worktree carries any change at all — the chip's amber ring."""
        return bool(self.modified or self.staged or self.untracked)


def _parse(text: str) -> GitState:
    """Turn ``git status --porcelain=v2 --branch`` output into a :class:`GitState`.

    The format is line-oriented and stable (git's own machine contract):

    - ``# branch.head <name>`` — the branch. ``# branch.ab`` is deliberately **not**
      read: it counts against the tracking branch, and this chip measures against
      origin/master (§ module docstring).
    - ``1 <XY> …`` ordinary change · ``2 <XY> …`` rename/copy — ``XY`` is the
      staged/worktree status pair, so a file can be counted in both columns (staged
      *and* modified) exactly as git reports it.
    - ``? <path>`` untracked · ``u …`` unmerged (counted as modified: it is work in
      the tree either way) · ``! <path>`` ignored (never counted).
    """
    branch = ''
    modified = staged = untracked = 0
    for line in text.splitlines():
        if line.startswith('# branch.head '):
            head = line.removeprefix('# branch.head ').strip()
            branch = '' if head == '(detached)' else head
        elif line.startswith('? '):
            untracked += 1
        elif line.startswith('u '):
            modified += 1
        elif line[:2] in ('1 ', '2 '):
            # XY: X = staged column, Y = worktree column; '.' means "nothing here".
            xy = line.split(' ', 2)[1]
            if len(xy) == 2:
                staged += xy[0] != '.'
                modified += xy[1] != '.'
    return GitState(branch=branch, modified=modified, staged=staged, untracked=untracked)


def _parse_divergence(text: str) -> tuple[int, int]:
    """``git rev-list --left-right --count origin/master...HEAD`` → (ahead, behind).

    The output is ``<left>\\t<right>``: left counts commits reachable from
    origin/master but not HEAD (**behind**), right the reverse (**ahead**).
    """
    fields = text.split()
    if len(fields) != 2:
        return 0, 0
    behind, ahead = fields
    return (int(ahead) if ahead.isdigit() else 0,
            int(behind) if behind.isdigit() else 0)


def filter_wired(repo_root: Path) -> bool:
    """Whether this clone has the clean/smudge filter registered in ``.git/config``.

    Public because the account page reports the same fact in its tools list
    (:mod:`solver.web.user.vault_api`) — one reader, so the header's chip and the
    account row cannot come to different conclusions about the same clone.

    Read from the file rather than asked of ``git config``: it is the same answer for
    the price of one small read instead of a second subprocess per page. The driver's
    name comes from :mod:`solver.crypto.config`, which owns every git-filter wire
    constant — this must not carry a second copy of it.

    Unreadable (or absent) reads as not wired — the conservative direction, since the
    chip's claim is "your private solutions are readable", never the reverse.
    """
    try:
        text = (repo_root / '.git' / 'config').read_text(encoding='utf-8', errors='replace')
    except OSError:
        return False
    return f'[filter "{crypto_config["filter_name"]}"]' in text


async def _git(repo_root: Path, *args: str) -> tuple[int, str]:
    """Run ``git *args`` in *repo_root* → (returncode, stdout). Never raises.

    A non-zero exit **logs git's own stderr**. That message is the whole diagnosis
    when a read fails on a clone this uid cannot open to look for itself — a dubious
    ownership refusal, a filter that died for want of the key, and a missing ref are
    three different problems with three different fixes, and identical exit codes.
    Discarding stderr here would leave only the code (128, always), which names none
    of them.
    """
    try:
        proc = await asyncio.create_subprocess_exec(
            'git', *args, cwd=str(repo_root),
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
    except (OSError, ValueError) as exc:
        log.warning('git state: cannot run git in %s: %s', repo_root, exc)
        return 1, ''
    try:
        raw_out, raw_err = await asyncio.wait_for(proc.communicate(), timeout=_TIMEOUT)
    except asyncio.TimeoutError:
        # The read outlived its welcome (a locked vault stalls the clean filter): kill
        # it, or it outlives the response too.
        proc.kill()
        await proc.wait()
        log.warning('git state: `git %s` timed out in %s', args[0], repo_root)
        return 1, ''
    if proc.returncode != 0:
        log.warning('git state: `git %s` exited %s in %s: %s', ' '.join(args),
                    proc.returncode, repo_root,
                    raw_err.decode('utf-8', errors='replace').strip() or '(no stderr)')
        return proc.returncode or 1, ''
    return 0, raw_out.decode('utf-8', errors='replace')


async def read(repo_root: Path) -> GitState | None:
    """This clone's state, or None when *repo_root* is not a git clone we can read.

    None is the "no chip" answer — no ``.git`` at all, or a uid without access to it
    (the shared content tier). A clone that *is* readable but will not answer comes
    back as ``GitState(unknown=True)``, which is a chip that says so.
    """
    if not (repo_root / '.git').exists():
        return None
    # --no-optional-locks: a page render must not take .git/index.lock out from under
    # the git commands the user is running in their own terminal (§ module docstring).
    rc, out = await _git(repo_root, '--no-optional-locks', 'status', '--porcelain=v2', '--branch')
    if rc != 0:
        return GitState(unknown=True)
    state = replace(_parse(out), filter_wired=filter_wired(repo_root))
    # Divergence from origin/master — the ref this workspace turns on. A clone with no
    # such ref (a fresh provision that has never fetched) is not an error: the branch
    # and the file counts are still true, so the chip drops the counts rather than the
    # whole state, and `upstream` stays empty to say the comparison was not made.
    rc, out = await _git(repo_root, 'rev-list', '--left-right', '--count',
                         f'{_UPSTREAM}...HEAD')
    if rc != 0:
        return state
    ahead, behind = _parse_divergence(out)
    return replace(state, upstream=_UPSTREAM, ahead=ahead, behind=behind)

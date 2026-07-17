#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The header chip's git state: one read of this user's clone.

The chip in the header (``_git.html``) answers three questions — what branch am I
on, how far is it from where it should be, and can I read the private solutions —
and this module answers them in **one** ``git status --porcelain=v2 --branch``.
That one command carries the branch, its upstream, the ahead/behind pair, and a
line per changed file, so the whole chip costs a single subprocess.

**Local refs only.** ``git status`` never touches the network, so ahead/behind are
measured against ``origin/master`` *as this clone last fetched it* — the freshness
of a ``git-sync``, not of the remote. That is the honest reading for a status light:
it reports the clone, and the clone is what the user's commands act on.

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

#: Ceiling on the status read. It is one local command, but it runs on the event
#: loop's watch and a wedged git (a locked vault, a stale index.lock) must not hold a
#: page render. Overrunning it reads as `unknown`, like any other failure.
_TIMEOUT: float = 5.0


@dataclass(frozen=True, slots=True)
class GitState:
    """One clone's state, as the header chip shows it.

    ``unknown`` is the honest zero value: the clone is there but git would not answer
    (a locked vault, a timeout, a detached HEAD with no upstream). Every field below
    it is then meaningless and the template shows none of them.
    """

    #: Current branch, e.g. ``user/vikas``. Empty on a detached HEAD.
    branch: str = ''
    #: The upstream it is measured against, e.g. ``origin/master``. Empty when unset.
    upstream: str = ''
    #: Commits on this branch that the upstream does not have (as of the last fetch).
    ahead: int = 0
    #: Commits on the upstream that this branch does not have (as of the last fetch).
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

    - ``# branch.head <name>`` / ``# branch.upstream <name>`` / ``# branch.ab +N -M``
    - ``1 <XY> …`` ordinary change · ``2 <XY> …`` rename/copy — ``XY`` is the
      staged/worktree status pair, so a file can be counted in both columns (staged
      *and* modified) exactly as git reports it.
    - ``? <path>`` untracked · ``u …`` unmerged (counted as modified: it is work in
      the tree either way) · ``! <path>`` ignored (never counted).
    """
    branch = upstream = ''
    ahead = behind = modified = staged = untracked = 0
    for line in text.splitlines():
        if line.startswith('# branch.head '):
            head = line.removeprefix('# branch.head ').strip()
            branch = '' if head == '(detached)' else head
        elif line.startswith('# branch.upstream '):
            upstream = line.removeprefix('# branch.upstream ').strip()
        elif line.startswith('# branch.ab '):
            for field in line.removeprefix('# branch.ab ').split():
                # '+N' ahead, '-M' behind. Anything else is not this line's business.
                if field.startswith('+'):
                    ahead = int(field[1:] or 0)
                elif field.startswith('-'):
                    behind = int(field[1:] or 0)
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
    return GitState(branch=branch, upstream=upstream, ahead=ahead, behind=behind,
                    modified=modified, staged=staged, untracked=untracked)


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


async def read(repo_root: Path) -> GitState | None:
    """This clone's state, or None when *repo_root* is not a git clone we can read.

    None is the "no chip" answer — no ``.git`` at all, or a uid without access to it
    (the shared content tier). A clone that *is* readable but will not answer comes
    back as ``GitState(unknown=True)``, which is a chip that says so.
    """
    if not (repo_root / '.git').exists():
        return None
    try:
        proc = await asyncio.create_subprocess_exec(
            'git', 'status', '--porcelain=v2', '--branch',
            cwd=str(repo_root),
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL,
        )
    except (OSError, ValueError):
        log.warning('git state: cannot run git in %s', repo_root)
        return GitState(unknown=True)
    try:
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=_TIMEOUT)
    except asyncio.TimeoutError:
        # The read outlived its welcome (a locked vault stalls the clean filter): kill
        # it, or it outlives the response too.
        proc.kill()
        await proc.wait()
        log.warning('git state: `git status` timed out in %s', repo_root)
        return GitState(unknown=True)
    if proc.returncode != 0:
        log.warning('git state: `git status` exited %s in %s', proc.returncode, repo_root)
        return GitState(unknown=True)
    state = _parse(stdout.decode('utf-8', errors='replace'))
    return replace(state, filter_wired=filter_wired(repo_root))

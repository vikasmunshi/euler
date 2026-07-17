#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The header chip's git state: three reads of this user's clone, by need.

The chip in the header (``_git.html``) answers three questions — what branch am I
on, how far is it from where it should be, and what is in my worktree — and the reads
are **staged by what each one needs**, so that a partial failure costs only the part
that failed:

1. ``git rev-parse --abbrev-ref HEAD`` — the branch. A pure ref read: no worktree
   scan, no filter, so it works with the vault locked. If even this fails the clone
   is genuinely unreadable (``unknown``).
2. ``git rev-list --left-right --count origin/master...HEAD`` — the divergence. Also
   refs only, no filter. **origin/master, always** — not the branch's own tracking
   branch (``origin/user/<slug>``, which answers "have I pushed?"), because the
   question this workspace turns on is "how far am I from **master**?", where work
   lands and ``git-sync`` closes the gap. Same ref ``scripts/git/status.sh`` uses;
   the two must not drift.
3. ``git status --porcelain=v2`` — the worktree file counts. The **one** read that
   scans files, so the one the clean filter can block: with the filter wired, git
   hashes ``solutions/private/**`` through it, and the filter needs the master key,
   which needs the vault. Right after login the vault is still locked — the browser
   posts ``/vault/unlock`` only *after* the first render — so this read fails there
   and the chip is ``worktree_unknown``: branch and divergence stand, the worktree
   line says "pending", and ``site.js`` refreshes it the moment the auto-unlock lands.
   (Before this staging the whole chip read "state not read" on every first load.)

**Freshness against the remote.** The divergence answers "how far am I from
origin/master?", and the honest answer is against the remote *as it is now*, not as
this clone last happened to fetch it — a clone that never fetches would read "level"
while the remote moved ahead (the reported bug). So :func:`read` takes *fetch*: when
set, it runs a throttled ``git fetch origin master`` before the count, exactly as
``scripts/git/status.sh`` does. The cost is a network round trip, so the caller spends
it only where it is worth blocking on — a full page load, the periodic poll, the chip's
own refresh — and not on content navigations, which read the local ref. ``git-sync``
fetches on its own, so after one the ref is already current (and the throttle skips a
redundant re-fetch). The branch and worktree reads never touch the network.

**No optional locks.** ``git status`` normally takes ``.git/index.lock`` to write
back the refreshed stat cache. This module is a *reader* on a page render, and the
user is typing real git commands into their terminal one pane away: a status read
that grabs the index lock can make their ``git-commit`` fail. ``--no-optional-locks``
is git's own answer for status displays — a little repeated hashing, no lock.

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
import time
from dataclasses import dataclass
from pathlib import Path

from solver.crypto.config import config as crypto_config

log = logging.getLogger('euler-content')

#: Ceiling on a local read. They run on the event loop's watch, and a wedged git (a
#: locked vault, a stale index.lock) must not hold a page render. Overrunning it reads
#: as `unknown`, like any other failure.
_TIMEOUT: float = 5.0

#: Tighter cap on the network fetch: it *blocks the render it runs on*, so a slow or
#: unreachable remote must fall back to the local ref rather than hang the load.
_FETCH_TIMEOUT: float = 4.0

#: A throttle floor on the fetch, keyed on `.git/FETCH_HEAD`'s mtime (which *any* fetch
#: resets — the chip's own, or the user's `git-sync`). It bounds fetch-spam from rapid
#: reloads, and means a full page load right after a `git-sync` does not re-fetch what
#: the sync just pulled. Well under the 10-minute poll, so a poll always fetches.
_FETCH_THROTTLE: float = 30.0

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
    #: True when the branch/divergence read succeeded but the **worktree scan** did not
    #: — the one part that touches files, so the one part the clean filter (and thus a
    #: locked vault) can block. The chip then shows branch + divergence and says the
    #: worktree state is pending, rather than blanking the whole chip or — worse —
    #: reading three zero counts as "clean". Distinct from ``unknown``: this is a chip
    #: that knows *most* of the answer.
    worktree_unknown: bool = False
    #: True when even the branch could not be read — the clone is there but git would
    #: not answer at all. The chip renders "state not read", not "clean".
    unknown: bool = False

    @property
    def dirty(self) -> bool:
        """Whether the worktree carries any change — the chip's amber ring.

        False, not None, when :attr:`worktree_unknown`: the ring must not appear on a
        state we could not read, and the template gates the whole worktree block on
        ``worktree_unknown`` before it ever consults this.
        """
        return bool(self.modified or self.staged or self.untracked)


def _parse_counts(text: str) -> tuple[int, int, int]:
    """``git status --porcelain=v2`` → (modified, staged, untracked).

    The format is line-oriented and stable (git's own machine contract):

    - ``1 <XY> …`` ordinary change · ``2 <XY> …`` rename/copy — ``XY`` is the
      staged/worktree status pair, so a file can be counted in both columns (staged
      *and* modified) exactly as git reports it.
    - ``? <path>`` untracked · ``u …`` unmerged (counted as modified: it is work in
      the tree either way) · ``! <path>`` ignored (never counted).

    The branch is **not** read here: it comes from a separate ``rev-parse`` that does
    not scan the worktree, so the chip keeps its branch even when this scan is blocked.
    """
    modified = staged = untracked = 0
    for line in text.splitlines():
        if line.startswith('? '):
            untracked += 1
        elif line.startswith('u '):
            modified += 1
        elif line[:2] in ('1 ', '2 '):
            # XY: X = staged column, Y = worktree column; '.' means "nothing here".
            xy = line.split(' ', 2)[1]
            if len(xy) == 2:
                staged += xy[0] != '.'
                modified += xy[1] != '.'
    return modified, staged, untracked


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


def _fetch_due(repo_root: Path) -> bool:
    """Whether origin/master is stale enough to re-fetch, by ``.git/FETCH_HEAD``'s mtime.

    Any fetch writes FETCH_HEAD — the chip's own *and* the user's ``git-sync`` — so this
    one mtime throttles them together: a load right after a sync does not re-fetch what
    the sync just pulled. A never-fetched clone (no FETCH_HEAD) is always due.
    """
    try:
        age = time.time() - (repo_root / '.git' / 'FETCH_HEAD').stat().st_mtime
    except OSError:
        return True
    return age > _FETCH_THROTTLE


async def _git(repo_root: Path, *args: str, timeout: float = _TIMEOUT) -> tuple[int, str]:
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
        raw_out, raw_err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
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


async def read(repo_root: Path, *, fetch: bool = False) -> GitState | None:
    """This clone's state, or None when *repo_root* is not a git clone we can read.

    None is the "no chip" answer — no ``.git`` at all, or a uid without access to it
    (the shared content tier). The reads are staged by what each one *needs*, so a
    vault that is still locked (the browser posts ``/vault/unlock`` only after the
    first render) costs the worktree counts, not the whole chip:

    1. **branch** — a pure ref read, no worktree scan, no filter. The spine: if even
       this fails the clone is genuinely unreadable → ``unknown``.
    2. **divergence** from origin/master — a pure ref walk, no filter. Absent only
       when there is no such ref (a fresh provision); the chip drops the counts, not
       the state.
    3. **worktree counts** — the one read that scans files, so the one the clean
       filter (a locked vault) can block → ``worktree_unknown``, branch + divergence
       kept.

    *fetch* asks for the divergence to be measured against the remote as it is *now*,
    not as this clone last saw it — a throttled ``git fetch origin master`` first, like
    ``scripts/git/status.sh``. The caller sets it for the moments worth a network round
    trip (a full page load, the periodic poll, the chip's own refresh) and leaves it off
    for content navigations, which read the local ref and never block on the network.
    """
    if not (repo_root / '.git').exists():
        return None
    rc, out = await _git(repo_root, 'rev-parse', '--abbrev-ref', 'HEAD')
    if rc != 0:
        return GitState(unknown=True)
    head = out.strip()
    branch = '' if head == 'HEAD' else head       # bare 'HEAD' == detached
    wired = filter_wired(repo_root)

    if fetch and _fetch_due(repo_root):
        # Best-effort and bounded: a failure or timeout (offline, slow remote) simply
        # leaves the local ref, which the rev-list below still reads — a stale count
        # beats a hung page. `origin master` with the default refspec updates
        # refs/remotes/origin/master, which is what the divergence is measured against.
        await _git(repo_root, 'fetch', '--quiet', 'origin', 'master', timeout=_FETCH_TIMEOUT)

    rc, out = await _git(repo_root, 'rev-list', '--left-right', '--count', f'{_UPSTREAM}...HEAD')
    if rc == 0:
        ahead, behind = _parse_divergence(out)
        upstream = _UPSTREAM
    else:
        ahead = behind = 0
        upstream = ''

    # --no-optional-locks: a page render must not take .git/index.lock out from under
    # the git commands the user is running in their own terminal (§ module docstring).
    rc, out = await _git(repo_root, '--no-optional-locks', 'status', '--porcelain=v2')
    if rc != 0:
        return GitState(branch=branch, upstream=upstream, ahead=ahead, behind=behind,
                        filter_wired=wired, worktree_unknown=True)
    modified, staged, untracked = _parse_counts(out)
    return GitState(branch=branch, upstream=upstream, ahead=ahead, behind=behind,
                    modified=modified, staged=staged, untracked=untracked, filter_wired=wired)

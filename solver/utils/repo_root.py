#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Where the working tree is — the one answer, for every part of the solver that needs it.

There were four derivations of this: :mod:`solver.config` (env, then a `git rev-parse`
anchored at the package dir, then hard failure), :mod:`solver.crypto.config` (the same, plus
a fallback), and the two web configs (a bare `parents[3]`). They drifted, and the drift
cost real access: with the git filter correctly running under `-P`, `__file__` moved out
of the checkout into `site-packages`, the package-anchored probe found no repository, and
the fallback — guarded only by "does it contain `solver/`", which `site-packages` also
does — adopted **site-packages itself** as the repo. The filter then reported the private key
missing from `/opt/euler/venv/lib/python3.14/.site-packages/id`: a confident answer from a
process that had no idea where the repo was.

So the order is fixed here, once:

1. **`EULER_REPO_ROOT`**, when set and a directory. The deployed tier points every service
   at the real tree with it, and the filter must agree with the shell about which tree that
   is. Nothing probes when this is set.
2. **the process cwd**, via `git rev-parse`. git runs a filter with the cwd at the *top of
   the worktree*, and the shell runs inside the checkout, so this is the authoritative answer
   for both — and the only one that works when the code is an installed package.
3. **this file's own directory**, via the same probe: an editable/dev checkout invoked from
   somewhere else entirely.
4. **this file two levels up**, but only if it *looks like the checkout* — `solver/` **and**
   `solutions/`. That second test is the lesson above: a wrong root is worse than no root,
   because it turns "I cannot tell where the repo is" into a plausible lie further downstream.

Otherwise it raises, naming the env var that settles it.

**Pure**: it captures git's output and changes nothing — no chdir, no PATH edits, no caching.
:mod:`solver.config` layers its own chdir on top; every other caller wants only the path.

Stdlib-only and silent on stdout at import, because :mod:`solver.crypto` is on the git-filter
path (where stdout carries file content) and must be able to import this.
"""
from __future__ import annotations

__all__ = ['REPO_ROOT_ENV', 'repo_root']

import os
from pathlib import Path
from subprocess import run

#: Env var naming the working tree explicitly — the deployed web tier sets it per service.
REPO_ROOT_ENV: str = 'EULER_REPO_ROOT'


def _probe(cwd: Path) -> Path | None:
    """Ask git for the worktree top from *cwd*, or None if it cannot say.

    git's own environment is shed first. Inherited from a git-spawned parent (a hook, a
    filter) `GIT_DIR` is set without `GIT_WORK_TREE`, and `rev-parse --show-toplevel`
    then reports the *cwd* as the toplevel — which for a probe anchored at a package
    directory yields `…/solver/crypto` as the repo root, and a secrets directory beside it
    that holds none of the user's keys.
    """
    probe_env = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
    try:
        result = run(['git', 'rev-parse', '--show-toplevel'], capture_output=True, text=True,
                     cwd=cwd, env=probe_env)
    except OSError:                       # git not installed at all, or cwd gone
        return None
    if result.returncode == 0 and (root := result.stdout.strip()):
        return Path(root)
    return None


def repo_root() -> Path:
    """Return the repository working-tree root (see the module docstring for the order).

    Raises:
        ValueError: if no candidate can be confirmed — which is the honest answer, and the
            message names `EULER_REPO_ROOT` as the way to settle it.
    """
    override = os.environ.get(REPO_ROOT_ENV, '').strip()
    if override and (from_env := Path(override)).is_dir():
        return from_env
    for candidate in (Path.cwd(), Path(__file__).parent):
        if (found := _probe(candidate)) is not None:
            return found
    fallback = Path(__file__).resolve().parents[2]
    if (fallback / 'solver').is_dir() and (fallback / 'solutions').is_dir():
        return fallback
    raise ValueError(f'failed to locate the repository root (set {REPO_ROOT_ENV}, '
                     'or run from inside the checkout)')

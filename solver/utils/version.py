#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The `version` command: report the running solver build's version."""
from __future__ import annotations

__all__ = ['version']

import subprocess

from solver.config import config
from solver.shell import console, register


def _git_detail() -> str | None:
    """Live ``git describe`` of ``config.root_dir``, or ``None`` when it has no git.

    Describes the clone the shell operates on (``config.root_dir``), which is the
    useful provenance in every context: the developer's checkout in a terminal, and
    each collaborator's own ``~/euler`` clone in the deployed per-user web shell —
    there the line answers "what commit is *my* clone on" alongside the frozen build
    number that ``config.version`` reports. Returns ``None`` only when ``root_dir``
    is not a git repo (or git is unavailable). Run live on every call — the clone's
    commit moves under a long-lived web shell (a git-sync, a commit), so a cached
    value would go stale.
    """
    try:
        proc = subprocess.run(
            ['git', '-C', str(config.root_dir), 'describe', '--tags', '--always', '--dirty', '--match', 'v*'],
            capture_output=True, text=True, timeout=2, check=False, cwd=config.root_dir,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


@register(requires='reader', help_text='Show the running solver build version.')
def version() -> int:
    """Print the installed build version, plus live git detail of the clone.

    The first line is the running build: the number recorded in the tracked
    `solver/version.py` (`config.version`), written only by the release script and
    correct even in the deployed venv where there is no git. The second line is the
    live `git describe`
    of `config.root_dir` — the developer's checkout in a terminal, or the
    collaborator's own `~/euler` clone in the web shell — reporting its exact
    commit and dirty state. The two answer different questions (what build is
    installed vs. what commit this clone sits on) and can legitimately differ.

    Reader-floor and read-only: no writes, no network, no vault access — safe to
    run in every collaborator's long-lived web shell.
    """
    console.print(f'[accent]solver {config.version}[/accent]')
    detail = _git_detail()
    if detail:
        console.print(f'[accent.dim]git {detail}[/accent.dim]')
    return 0

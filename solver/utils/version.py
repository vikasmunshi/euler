#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The `version` command: report the running solver build's version."""
from __future__ import annotations

__all__ = ['version']

import subprocess
from functools import cache
from pathlib import Path

import solver
from solver.config import config
from solver.shell import console, register


@cache
def _git_detail() -> str | None:
    """Live ``git describe`` for an editable checkout, or ``None`` when detached.

    Keyed on the **package** location (``solver.__file__``), not the shell's cwd:
    the deployed web shell runs from ``/opt/euler/venv`` — a plain install with no
    ``.git`` — so this returns ``None`` there and the frozen wheel version stands
    alone (it deliberately does *not* describe the user's ``~/euler`` clone that
    happens to be the cwd). In an editable dev checkout it adds the live
    ``-<n>-g<sha>[-dirty]`` suffix. Cached: computed once per process.
    """
    tree = Path(solver.__file__).resolve().parent.parent
    try:
        proc = subprocess.run(
            ['git', '-C', str(tree), 'describe', '--tags', '--always', '--dirty', '--match', 'v*'],
            capture_output=True, text=True, timeout=2, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


@register(requires='reader', help_text='Show the running solver build version.')
def version() -> int:
    """Print the installed package version, plus live git detail in a checkout.

    The version comes from the wheel metadata frozen at build time
    (`config.version` → `importlib.metadata`), so it is correct in the detached
    deployed venv where there is no git. In an editable dev checkout the live
    `git describe` detail is appended for the exact commit and dirty state.

    Reader-floor and read-only: no writes, no network, no vault access — safe to
    run in every collaborator's long-lived web shell.
    """
    console.print(f'[accent]solver {config.version}[/accent]')
    detail = _git_detail()
    if detail:
        console.print(f'[accent.dim]git {detail}[/accent.dim]')
    return 0

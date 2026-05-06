#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Git operations for the solver repository: publish, refresh, and status."""
from __future__ import annotations

from subprocess import CalledProcessError, run
from typing import Literal

from solver.config import ColorCodes, root_dir

publish_script: str = './scripts/git-publish.sh'
refresh_script: str = './scripts/git-refresh.sh'
status_script: str = './scripts/git-status.sh'


def run_cmdline(cmdline: str) -> None:
    """Run a shell command in the repository root and print its exit code.

    Args:
        cmdline: The shell command string to execute.
    """
    try:
        process = run(cmdline, shell=True, check=True, cwd=root_dir)
    except CalledProcessError as e:
        result: int = e.returncode
    else:
        result = process.returncode
    print(f'> {cmdline} -> {ColorCodes.GREEN if result == 0 else ColorCodes.RED}{result}{ColorCodes.RESET}')


def git_publish(*targets: Literal['keys', 'scripts', 'solutions', 'solver'], dry_run: bool = False) -> None:
    """Publish changed files for named targets to the remote repository.

    Args:
        targets: Scopes of files to publish — one or more of 'keys', 'scripts', 'solutions', or 'solver'.
        dry_run: Print the push and pull-request commands instead of running them.  Defaults to False.

    Raises:
        ValueError: If any target is not one of the accepted values.
    """
    if not all(target in ['keys', 'scripts', 'solutions', 'solver'] for target in targets):
        raise ValueError(f'Invalid targets: {", ".join(targets)}')
    if dry_run:
        run_cmdline(f'{publish_script} --dry-run {" ".join(targets)}')
    else:
        run_cmdline(f'{publish_script} {" ".join(targets)}')


def git_refresh(dry_run: bool = False) -> None:
    """Bring the local repository in sync with origin/master.

    Args:
        dry_run: Print the sync commands instead of running them. Defaults to False.
    """
    if dry_run:
        run_cmdline(f'{refresh_script} --dry-run')
    else:
        run_cmdline(refresh_script)


def git_status(details: bool = False) -> None:
    """Display the sync state between the local branch and origin/master.

    Args:
        details:    When True, lists every differing file and uncommitted change.
                    When False (default), shows file counts only.
    """
    if details:
        run_cmdline(status_script)
    else:
        run_cmdline(f'{status_script} --summary')


__all__ = (
    'git_publish',
    'git_refresh',
    'git_status',
)

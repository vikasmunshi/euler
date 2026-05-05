#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" git utilities for solver"""
from __future__ import annotations

from subprocess import CalledProcessError, run
from typing import Literal

from solver.config import ColorCodes, root_dir

publish_script: str = './solver/data/publish.sh'
refresh_script: str = './solver/data/refresh.sh'
status_script: str = './solver/data/status.sh'


def run_cmdline(cmdline: str) -> None:
    """Run a command line in the root directory."""
    try:
        process = run(cmdline, shell=True, check=True, cwd=root_dir)
    except CalledProcessError as e:
        result: int = e.returncode
    else:
        result = process.returncode
    print(f'> {cmdline} -> {ColorCodes.GREEN if result == 0 else ColorCodes.RED}{result}{ColorCodes.RESET}')


def git_publish(target: Literal['keys', 'scripts', 'solver', 'solutions'], dry_run: bool = True) -> None:
    """Publish changes to the remote repository.

    Args:
        target (Literal['keys', 'scripts', 'solver', 'solutions']): The target to publish.
        dry_run (bool, optional): Whether to perform a dry run. Defaults to True.
    """
    if target not in ['keys', 'scripts', 'solver', 'solutions']:
        raise ValueError(f'Invalid target: {target}')
    if dry_run:
        run_cmdline(f'{publish_script} --dry-run {target}')
    else:
        run_cmdline(f'{publish_script} {target}')


def git_refresh(dry_run: bool = True) -> None:
    """Refresh the local repository.

    Args:
        dry_run (bool, optional): Whether to perform a dry run. Defaults to True.
    """
    if dry_run:
        run_cmdline(f'{refresh_script} --dry-run')
    else:
        run_cmdline(refresh_script)


def git_status(details: bool = False) -> None:
    """ Shows git status. The status may display detailed information or a summary based on the input parameter.

    Args:
        details (bool): If set to True, displays detailed status information.
                        If False, displays a summary.
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

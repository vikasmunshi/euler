#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Problem browser: opens local HTML problem pages in the default web browser.

Relies on a "browser" executable being present on "PATH" (see
"scripts/setup_chrome.sh").  Availability is probed once and cached.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from subprocess import CalledProcessError, run

from solver.config import workspace_dir
from solver.stack import stack_path
from solver.util.utils import canonical_path


@lru_cache(maxsize=None)
def browser_is_available() -> bool:
    """Return "True" if the "browser" executable is present on "PATH".

    The result is cached after the first call.
    """
    try:
        run('command browser -h 1>/dev/null 2>&1', shell=True, check=True)
        return True
    except CalledProcessError:
        return False


def show_in_browser(problem_number: int = 0) -> None:
    """Open a problem's "problem.html" in the system browser.

    When *problem_number* is "0" (default), opens the workspace copy
    ("workspace_dir/problem.html").

    Prints an error and returns early if:
    - the "browser" command is not available, or
    - the resolved "problem.html" file does not exist.

    Arguments:
        problem_number: Problem to open; "0" means the current workspace.
    """
    if not browser_is_available():
        print('Error: "browser" command not available; use scripts/setup_chrome.sh to install Chrome')
        return
    if problem_number == 0:
        filepath: Path = workspace_dir / 'problem.html'
    else:
        filepath = stack_path(problem_number, 'problem.html')[1]
    if not filepath.exists():
        if problem_number == 0:
            print('Error: workspace is empty; use init <problem_number> to initialize it')
            return
        print(f'Error: {canonical_path(filepath)} does not exist')
        return
    run(f'browser open {filepath.as_posix()!r}', shell=True)


__all__ = ('show_in_browser',)

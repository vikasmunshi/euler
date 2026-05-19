#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Problem browser: opens local HTML problem pages in the default web browser. """
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from subprocess import CalledProcessError, run

from solver.core.config import config
from solver.core.stack import stack_path
from solver.core.console import console, register
from solver.utils.path_utils import canonical_path


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


@register(name='browser',
          help='Open the problem page in a browser; number=0 opens the summary.',
          usage='browser [problem_number]',
          aliases=('open', 'show', 'view'))
def show_in_browser(problem_number: int = 0) -> None:
    """Open a problem's "problem.html" in the system browser.

    When *problem_number* is "0" (default), opens the summary page.

    Prints an error and returns early if:
    - the "browser" command is not available, or
    - the resolved "problem.html" file does not exist.

    Arguments:
        problem_number: Problem to open; "0" means the current workspace.
    """
    if not browser_is_available():
        console.print('[error]error:[/error] [muted]"browser" command not available; '
                      'use [accent]solver sys-install chrome[/accent] to install Chrome[/muted]')
        return
    if problem_number == 0:
        filepath: Path = config.solutions_summary_file
    else:
        filepath = stack_path(problem_number, 'problem.html')[1]
    if not filepath.exists():
        if problem_number == 0:
            console.print('[error]error:[/error] [muted]workspace is empty; '
                          'use [accent]init <problem_number>[/accent] to initialize it[/muted]')
            return
        console.print(f'[error]error:[/error] [muted]{canonical_path(filepath)} does not exist[/muted]')
        return
    run(f'browser open {filepath.as_posix()!r}', shell=True)


__all__ = ('show_in_browser',)

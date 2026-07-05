#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Open a problem or its files in the web front end: the `show` and `edit` commands.

Both drive the same profile-aware bridge to the browser — the in-page viewer panel
(web profile) or a named browser tab (terminal profile) — differing only in the URL:

- `show` opens a problem's rendered documentation page (`<base_url>/NNNN/`).
- `edit` opens a solution file in the code editor (`<base_url>/edit/NNNN/<file>`).
"""
from __future__ import annotations

__all__ = ['show', 'edit']

import mimetypes
import sys
import time
from functools import lru_cache
from pathlib import Path
from subprocess import CalledProcessError, DEVNULL, run
from typing import Iterable

from prompt_toolkit.completion import Completion

from solver.config import ExitCodes, config
from solver.core.problems import Problem
from solver.shell import console, register
from solver.shell.command import Context
from solver.shell.variables import variables
from solver.utils.path_utils import iterdir_recursive
from solver.web.cli import ensure_running

#: OSC identifier shared with solver.js's `registerOscHandler`: `ESC ] 5379 ; <payload> BEL`.
#: `open;<NNNN>;<token>` (show) or `edit;<NNNN>;<token>;<relpath>` (edit).
_OSC_CODE: int = 5379


# ---------------------------------------------------------------------------
# Browser
# ---------------------------------------------------------------------------

@lru_cache(maxsize=None)
def _browser_is_available() -> bool:
    """Return "True" if the "browser" executable is present on "PATH".

    The result is cached after the first call.
    """
    try:
        run('command browser -h 1>/dev/null 2>&1', shell=True, check=True, stdout=DEVNULL, stderr=DEVNULL)
        return True
    except CalledProcessError:
        return False


def _browser_unavailable_error() -> int:
    """Report the missing `browser` command and return the error exit code."""
    console.print('[error]error:[/error] [muted]"browser" command not available; '
                  'use [accent]solver install chrome[/accent] to install Chrome[/muted]')
    return ExitCodes.EXIT_ERROR


# ---------------------------------------------------------------------------
# edit — open a solution file in the code editor
# ---------------------------------------------------------------------------

def _target_problem(ctx: Context) -> Problem:
    """The problem whose files `edit` completes: a leading numeric arg, else the current one.

    Mirrors the adapter's `problem` special — the first positional token naming a
    known problem selects it (so `edit 42 <tab>` lists problem 42's files); with no
    such token the completions come from `variables.problem`, the active problem.
    """
    for tok in ctx.argv:
        if tok.isdigit():
            try:
                return Problem.from_number(int(tok))
            except ValueError:
                break
    return variables.problem


def _solution_file_completions(ctx: Context, incomplete: str) -> Iterable[str | Completion]:
    """Filename completions for `edit`: the target problem's files, as `ls` lists them.

    The candidates are the solution-directory files with a guessable mimetype (the
    same set `ls` shows), each as a POSIX path relative to the solution directory —
    the form `edit`/the web viewer expect. The adapter prefix-filters them.
    """
    problem = _target_problem(ctx)
    return sorted(
        name for name in iterdir_recursive(problem.solution_dir, rt='str')
        if mimetypes.guess_type(name)[0] is not None
    )


@register(help_text='Open a solution file in the web code editor.',
          aliases=('ed',), pass_ctx=True, quietable=True,
          completers={'filename': _solution_file_completions})
def edit(ctx: Context, problem: Problem, filename: str) -> int:
    """Open *filename* from *problem*'s solution directory in the web code editor.

    The counterpart to `show` (which opens the rendered problem): *problem* defaults
    to the current problem, and *filename* completes to the files `ls` lists. The
    file must already exist — run `new` to create a solution first. Profile-aware,
    like `show`:

    - **web** — emits an `OSC 5379` `edit` sequence (`edit;<NNNN>;<token>;<relpath>`)
      that the xterm.js page rides over the PTY → WebSocket pipe to point its viewer
      panel at the file's editor (`<origin>/edit/NNNN/<relpath>`).

    - **terminal** — auto-starts `solver-web` and opens that editor URL in the named
      browser tab "solver-edit" (via `browser open-in-tab`); errors early if the
      `browser` command is unavailable.

    Arguments:
        ctx:      The shell's command context (selects the profile-specific path).
        problem:  The problem owning the file; defaults to the current problem.
        filename: The solution-directory file to edit (as `ls` lists it).
    """
    if '..' in Path(filename).parts or Path(filename).is_absolute() \
            or not (problem.solution_dir / filename).is_file():
        console.print(f'[error]error:[/error] [muted]{filename} not found in '
                      f'[accent]{problem.number:04d}[/accent]; run [accent]new[/accent] '
                      'to create a solution[/muted]')
        return ExitCodes.EXIT_ERROR
    rel: str = Path(filename).as_posix()

    if ctx.shell.profile == 'web':
        token = time.time_ns() // 1_000_000
        sys.stdout.write(f'\x1b]{_OSC_CODE};edit;{problem.number:04d};{token};{rel}\x07')
        sys.stdout.flush()
        console.print(f'[muted]editing[/muted] [accent]{rel}[/accent] '
                      '[muted]in the viewer panel[/muted]')
        return ExitCodes.EXIT_OK

    if not _browser_is_available():
        return _browser_unavailable_error()
    ensure_running()
    url: str = f'{config.base_url}/edit/{problem.number:04d}/{rel}'
    pipe = DEVNULL if console.quiet else None
    run(f'browser open-in-tab solver-edit {url}', shell=True, stdout=pipe, stderr=pipe)
    return ExitCodes.EXIT_OK


# ---------------------------------------------------------------------------
# show — open the rendered documentation page
# ---------------------------------------------------------------------------

@register(help_text='Open problem/file in a browser or the web viewer panel.',
          aliases=('open', 'view'), pass_ctx=True, quietable=True,
          completers={'filename': _solution_file_completions})
def show(ctx: Context, problem: Problem, filename: str | None = None) -> int:
    """Open a problem's documentation page, in a browser or the web viewer panel.

    When *problem* is omitted, opens the current problem. The path depends on the
    shell profile:

    - **terminal** — auto-starts the `solver-web` server and opens its page for the
      problem (`<base_url>/NNNN/`) in the named browser tab "solver-doc" (via
      `browser open-in-tab`). Every `show` reuses that one tab: the same problem is
      focused and refreshed, a different problem navigates the tab in place, and the
      tab is recreated if it has been closed. Prints an error and returns early if
      the "browser" command is not available.

    - **web** — the shell has no local browser to drive (it runs on the server while
      the user's browser is elsewhere), so it emits an `OSC 5379` control sequence
      (`open;<NNNN>;<token>`) on stdout. The xterm.js page rides it over the
      PTY → WebSocket pipe and points its in-page viewer iframe at `<origin>/NNNN/`;
      the monotonic token lets the page ignore the sequence when the PTY replay
      buffer re-sends it on reconnect.

    When *filename* is given, `show` opens that solution file in the code editor
    instead of the rendered page — it delegates to `edit`, so the same file lookup,
    profile handling, and browser tab apply.

    Arguments:
        ctx:      The shell's command context (selects the profile-specific path).
        problem:  The `problem` to open; defaults to the current problem.
        filename: A solution file to open in the code editor; when omitted, opens
                  the rendered documentation page instead.
    """
    if filename is not None:
        return edit(ctx, problem, filename)

    if ctx.shell.profile == 'web':
        token = time.time_ns() // 1_000_000
        sys.stdout.write(f'\x1b]{_OSC_CODE};open;{problem.number:04d};{token}\x07')
        sys.stdout.flush()
        console.print(f'[muted]opening[/muted] [accent]{problem.number:04d}[/accent] '
                      '[muted]in the viewer panel[/muted]')
        return ExitCodes.EXIT_OK

    if not _browser_is_available():
        return _browser_unavailable_error()
    ensure_running()
    url: str = f'{config.base_url}/{problem.number:04d}/'
    pipe = DEVNULL if console.quiet else None
    run(f'browser open-in-tab solver-doc {url}', shell=True, stdout=pipe, stderr=pipe)
    return ExitCodes.EXIT_OK

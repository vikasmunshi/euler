#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Open a problem or its files in the web front end: the `show` and `edit` commands.

Both drive the same channel-aware bridge to the browser — the app shell's left pane
(web channel, over the terminal's OSC pipe) or a named browser tab (terminal
channel) — differing only in the URL. The channel is the resolved subject's
(`config.subject.channel`), never a CLI flag:

- `show` opens a problem's rendered documentation page (`<base_url>/solutions/NNNN/`).
- `edit` opens a solution file in the code editor (`<base_url>/edit/solutions/NNNN/<file>`).
"""
from __future__ import annotations

__all__ = ['show', 'edit']

import mimetypes
from functools import lru_cache
from pathlib import Path
from subprocess import CalledProcessError, DEVNULL, run
from typing import Annotated, Iterable

from prompt_toolkit.completion import Completion

from solver.config import ExitCodes, config
from solver.core import osc
from solver.core.problems import Problem
from solver.shell import console, register
from solver.shell.command import Context
from solver.shell.dialogue import Ask
from solver.shell.variables import variable, variables
from solver.utils.path_utils import iterdir_recursive


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


def _files_of(problem: Problem) -> list[str]:
    """*problem*'s solution-directory files, as `ls` lists them.

    The files with a guessable mimetype, each as a POSIX path relative to the solution
    directory — the form `edit` and the web viewer expect.
    """
    return sorted(name for name in iterdir_recursive(problem.solution_dir, rt='str')
                  if mimetypes.guess_type(name)[0] is not None)


@variable("the current problem's solution files")
def solution_files() -> list[str]:
    """The files of the problem the shell is working on.

    The current problem, because that is what a variable can know: by the time a menu is
    put the adapter has already settled which problem the command acts on, so `edit 42`
    offers 42's files. In a block, `loop {solution_files}:` walks the workspace problem's.
    """
    return _files_of(variables.problem)


def _solution_file_completions(ctx: Context, incomplete: str) -> Iterable[str | Completion]:
    """Filename completions for `edit`: the target problem's files, as `ls` lists them.

    Reads the problem from the tokens typed so far rather than the workspace one, so
    `edit 42 <TAB>` completes 42's files before the command has run. The adapter
    prefix-filters them.
    """
    return _files_of(_target_problem(ctx))


@register(requires='contributor', aliases=('ed',), quietable=True, completers={'filename': _solution_file_completions})
def edit(problem: Problem,
         filename: Annotated[str, Ask('Which file?', choices='solution_files',
                                      empty='no files in this problem yet — run `new`')]) -> int:
    """Open a solution file in the web code editor.

    The counterpart to `show` (which opens the rendered problem): *problem* defaults
    to the current problem, and *filename* completes to the files `ls` lists. The
    file must already exist — run `new` to create a solution first. Channel-aware,
    like `show` (the channel is the resolved subject's):

    - **web** — emits an `OSC 5379` `edit` sequence (`edit;<NNNN>;<token>;<relpath>`)
      that the xterm.js page rides over the PTY → WebSocket pipe to point the app
      shell's left pane at the file's editor (`<origin>/edit/solutions/NNNN/<relpath>`).

    - **terminal** — opens that editor URL in the named browser tab "solver-edit"
      (via `browser open-in-tab`); errors early if the `browser` command is
      unavailable.

    Args:
        problem: [problem] The problem owning the file.
        filename: [asked] The solution-directory file to edit, as `ls` lists it. Offered
            as a menu when omitted. It must already
            exist.
    """
    if '..' in Path(filename).parts or Path(filename).is_absolute() \
            or not (problem.solution_dir / filename).is_file():
        console.print(f'[error]error:[/error] [muted]{filename} not found in '
                      f'[accent]{problem.number:04d}[/accent]; run [accent]new[/accent] '
                      'to create a solution[/muted]')
        return ExitCodes.EXIT_ERROR
    rel: str = Path(filename).as_posix()

    if config.subject.channel == 'web':
        osc.emit('edit', f'{problem.number:04d}', str(osc.token()), rel)
        console.print(f'[muted]editing[/muted] [accent]{rel}[/accent] '
                      '[muted]in the viewer panel[/muted]')
        return ExitCodes.EXIT_OK

    if not _browser_is_available():
        return _browser_unavailable_error()
    url: str = f'{config.base_url}/edit/solutions/{problem.number:04d}/{rel}'
    pipe = DEVNULL if console.quiet else None
    run(f'browser open-in-tab solver-edit {url}', shell=True, stdout=pipe, stderr=pipe)
    return ExitCodes.EXIT_OK


# ---------------------------------------------------------------------------
# show — open the rendered documentation page
# ---------------------------------------------------------------------------

@register(requires='reader', aliases=('open', 'view'), quietable=True,
          completers={'filename': _solution_file_completions})
def show(problem: Problem, filename: str | None = None) -> int:
    """Open a problem's documentation page, in a browser or the web viewer panel.

    When *problem* is omitted, opens the current problem. The path depends on the
    shell's channel (from the resolved subject):

    - **terminal** — opens the problem's page (`<base_url>/solutions/NNNN/`) in the named
      browser tab "solver-doc" (via
      `browser open-in-tab`). Every `show` reuses that one tab: the same problem is
      focused and refreshed, a different problem navigates the tab in place, and the
      tab is recreated if it has been closed. Prints an error and returns early if
      the "browser" command is not available.

    - **web** — the shell has no local browser to drive (it runs on the server while
      the user's browser is elsewhere), so it emits an `OSC 5379` control sequence
      (`open;<NNNN>;<token>`) on stdout. The xterm.js page rides it over the
      PTY → WebSocket pipe and swaps the app shell's left pane to
      `<origin>/solutions/NNNN/`; the monotonic token lets the page ignore the
      sequence when the PTY replay buffer re-sends it on reconnect.

    When *filename* is given, `show` opens that solution file in the code editor
    instead of the rendered page — it delegates to `edit`, so the same file lookup,
    channel handling, and browser tab apply.

    Args:
        problem: [problem] The problem to open.
        filename: A solution file to open in the code editor instead. Defaults to None,
            which opens the rendered documentation page.
    """
    if filename is not None:
        return edit(problem, filename)

    if config.subject.channel == 'web':
        osc.emit('open', f'{problem.number:04d}', str(osc.token()))
        console.print(f'[muted]opening[/muted] [accent]{problem.number:04d}[/accent] '
                      '[muted]in the viewer panel[/muted]')
        return ExitCodes.EXIT_OK

    if not _browser_is_available():
        return _browser_unavailable_error()
    url: str = f'{config.base_url}/solutions/{problem.number:04d}/'
    pipe = DEVNULL if console.quiet else None
    run(f'browser open-in-tab solver-doc {url}', shell=True, stdout=pipe, stderr=pipe)
    return ExitCodes.EXIT_OK

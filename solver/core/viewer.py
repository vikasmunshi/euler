#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Open a problem or its files in the web front end: the `show` and `edit` commands.

Both drive the same channel-aware bridge to the browser — the app shell's left pane
(web channel, over the terminal's OSC pipe) or a named browser tab (terminal
channel) — differing only in the URL. The channel is the resolved subject's
(`config.subject.channel`), never a CLI flag:

- `show` opens a problem's rendered documentation page (`<base_url>/solutions/NNNN/`),
  or any site page given its relative path (`<base_url>/<path>`).
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
# show — open the rendered documentation page, or any site page
# ---------------------------------------------------------------------------

#: The site routes `show <path>` may swap the pane to: its first segment must be one of
#: these. Left out on purpose — `terminal` (the shell would frame itself), `git` (a
#: header fragment, not a page) and `story` (the deck opens in a tab of its own).
PANE_ROUTES: tuple[str, ...] = ('solutions', 'topics', 'docs', 'about', 'edit', 'account', 'shell')


def _pane_path_error(path: str) -> str | None:
    """Why *path* is not a relative web path `show` may open, or None if it is.

    Shape first — relative, no `.`/`..` or empty segments (a trailing `/` is fine:
    `topics/` is the canonical index), no query, fragment, backslash, whitespace or
    control characters — then the first segment must name a :data:`PANE_ROUTES`
    route. Whether the page exists is the site's to say: a miss is its 404, in the pane.
    """
    if not path or path.startswith('/'):
        return 'must be a relative path (no leading /)'
    if any(ch in path for ch in '?#\\') or any(ch.isspace() or not ch.isprintable() for ch in path):
        return 'must be a plain path (no query, fragment, backslash or whitespace)'
    segments = path.removesuffix('/').split('/')
    if any(seg in ('', '.', '..') for seg in segments):
        return 'must not contain empty, . or .. segments'
    if segments[0] not in PANE_ROUTES:
        return f'must start with one of: {", ".join(PANE_ROUTES)}'
    return None


def _pane_path_completions(ctx: Context, incomplete: str) -> Iterable[str | Completion]:
    """Path completions for `show`: the pane routes, then topic pages under `topics/`.

    The topic pages are the articles' paths under `topics/` without their `.md` — the
    route the site serves them at. The adapter prefix-filters them.
    """
    if not incomplete.startswith('topics/'):
        return [f'{route}/' for route in PANE_ROUTES]
    return sorted(f'topics/{name.removesuffix(".md")}'
                  for name in iterdir_recursive(config.topics_dir, rt='str') if name.endswith('.md'))


@register(requires='reader', aliases=('open', 'view'), quietable=True,
          completers={'path': _pane_path_completions})
def show(problem: Problem, path: str | None = None) -> int:
    """Open a problem's page, or any site page, in a browser or the web viewer panel.

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

    When *path* is given, `show` opens that site page instead of the problem's —
    `show topics/technique/concatenation` — over the same channels (`nav;<token>;<path>`
    on web, the "solver-doc" tab on a terminal). The page ignores *problem*, but naming
    one still makes it the current problem: `show 121 topics/…` selects 121.

    Args:
        problem: [problem] The problem to open (and select as the current problem).
        path: A relative site path to open instead, e.g. `topics/technique/concatenation`.
            Its first segment must be one of solutions, topics, docs, about, edit,
            account or shell. Defaults to None, which opens the problem's page.
    """
    if path is not None:
        if (why := _pane_path_error(path)) is not None:
            console.print(f'[error]error:[/error] [muted]{path}: {why}[/muted]')
            return ExitCodes.EXIT_ERROR
        target, label, fields = f'/{path}', path, (str(osc.token()), path)
    else:
        number = f'{problem.number:04d}'
        target, label, fields = f'/solutions/{number}/', number, (number, str(osc.token()))

    if config.subject.channel == 'web':
        osc.emit('nav' if path is not None else 'open', *fields)
        console.print(f'[muted]opening[/muted] [accent]{label}[/accent] '
                      '[muted]in the viewer panel[/muted]')
        return ExitCodes.EXIT_OK

    if not _browser_is_available():
        return _browser_unavailable_error()
    pipe = DEVNULL if console.quiet else None
    run(f'browser open-in-tab solver-doc {config.base_url}{target}', shell=True, stdout=pipe, stderr=pipe)
    return ExitCodes.EXIT_OK

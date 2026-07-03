#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Browser utilities for visualizing solutions."""
from __future__ import annotations

__all__ = ['show']

import sys
import time
from functools import lru_cache
from subprocess import CalledProcessError, DEVNULL, run

from solver.config import ExitCodes, config
from solver.core.problems import Problem
from solver.shell import console, register
from solver.shell.command import Context
from solver.web.cli import ensure_running

#: OSC identifier shared with solver.js's `registerOscHandler`: `ESC ] 5379 ; <payload> BEL`.
_OSC_CODE: int = 5379


# ---------------------------------------------------------------------------
# Browser
# ---------------------------------------------------------------------------

@lru_cache(maxsize=None)
def browser_is_available() -> bool:
    """Return "True" if the "browser" executable is present on "PATH".

    The result is cached after the first call.
    """
    try:
        run('command browser -h 1>/dev/null 2>&1', shell=True, check=True, stdout=DEVNULL, stderr=DEVNULL)
        return True
    except CalledProcessError:
        return False


@register(help_text='Open documentation in a browser or the web viewer panel.',
          aliases=('open', 'view'), pass_ctx=True, quietable=True)
def show(ctx: Context, problem: Problem) -> int:
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

    Arguments:
        ctx:      The shell's command context (selects the profile-specific path).
        problem:  The `problem` to open; defaults to the current problem.
    """
    if ctx.shell.profile == 'web':
        token = time.time_ns() // 1_000_000
        sys.stdout.write(f'\x1b]{_OSC_CODE};open;{problem.number:04d};{token}\x07')
        sys.stdout.flush()
        console.print(f'[muted]opening[/muted] [accent]{problem.number:04d}[/accent] '
                      '[muted]in the viewer panel[/muted]')
        return ExitCodes.EXIT_OK

    if not browser_is_available():
        console.print('[error]error:[/error] [muted]"browser" command not available; '
                      'use [accent]solver install chrome[/accent] to install Chrome[/muted]')
        return ExitCodes.EXIT_ERROR
    ensure_running()
    url: str = f'{config.base_url}/{problem.number:04d}/'
    pipe = DEVNULL if console.quiet else None
    run(f'browser open-in-tab solver-doc {url}', shell=True, stdout=pipe, stderr=pipe)
    return ExitCodes.EXIT_OK

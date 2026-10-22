#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The web shell's `show` and `edit`: swap the app shell's left pane instead of opening a tab.

Replacement bodies (`overlays.toml` → `replace`) for :func:`solver.core.viewer.show` and
:func:`solver.core.viewer.edit`. The shell runs on the server while the user's browser is
elsewhere, so there is no local browser to drive: each emits an `OSC 5379` sequence on stdout
that the xterm.js page rides over the PTY → WebSocket pipe, and the page swaps its left pane —
the monotonic token lets it ignore the sequence when the PTY replay buffer re-sends it on
reconnect. What may be opened is decided by the solver's own checks, so the two bodies agree.

The signatures are the originals' exactly — :func:`solver.shell.register.replace_body` refuses
anything else — while the help, usage and completion stay the originals'.
"""
from __future__ import annotations

__all__ = ['edit', 'show']

from solver.config import ExitCodes
from solver.core.problems import Problem
from solver.core.viewer import edit_path, pane_path_error
from solver.shell import console
from euler_webshell.shell import osc


def edit(problem: Problem, filename: str) -> int:
    """Point the left pane at *filename*'s editor: `edit;<NNNN>;<token>;<relpath>`."""
    if (rel := edit_path(problem, filename)) is None:
        return ExitCodes.EXIT_ERROR
    osc.emit('edit', f'{problem.number:04d}', str(osc.token()), rel)
    console.print(f'[muted]editing[/muted] [accent]{rel}[/accent] [muted]in the viewer panel[/muted]')
    return ExitCodes.EXIT_OK


def show(problem: Problem, path: str | None = None) -> int:
    """Swap the left pane to the problem's page (`open;<NNNN>;<token>`) or to *path* (`nav;<token>;<path>`)."""
    if path is not None:
        if (why := pane_path_error(path)) is not None:
            console.print(f'[error]error:[/error] [muted]{path}: {why}[/muted]')
            return ExitCodes.EXIT_ERROR
        label = path
        osc.emit('nav', str(osc.token()), path)
    else:
        label = f'{problem.number:04d}'
        osc.emit('open', label, str(osc.token()))
    console.print(f'[muted]opening[/muted] [accent]{label}[/accent] [muted]in the viewer panel[/muted]')
    return ExitCodes.EXIT_OK

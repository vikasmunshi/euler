#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The web shell: the solver shell, extended for a PTY framed by the browser.

The solver shell runs standalone and knows nothing of the web. This package composes it with
an :class:`~solver.shell.extension.Extension` (docs/package-split.md § 3.2): the overlay table
`overlays.toml` makes the state-changing commands nudge the page over `OSC 5379`
(:mod:`solver.web.shell.osc`) and replaces `show` / `edit` with bodies that swap the app
shell's left pane (:mod:`solver.web.shell.viewer`). The session's identity is a one-time ticket
(:mod:`solver.web.shell.identity`), the vault is never prompted for (the browser unlocks it), and
the shell syncs the clone with origin before its first prompt. The PTY runs
`python -m solver.web.shell`.
"""
from __future__ import annotations

__all__ = ['OVERLAYS_FILE', 'extension', 'sync_at_start']

from pathlib import Path
from typing import Callable

from solver.shell.extension import Extension, ExtensionError, read_overlays
from solver.shell.tty import console
from solver.web.shell import osc
from solver.web.shell.identity import ticket_subject

#: The overlay table, shipped as package data.
OVERLAYS_FILE: Path = Path(__file__).with_name('overlays.toml')


def extension() -> Extension:
    """The web shell's extension; an overlay emitting an event :mod:`osc` cannot send is refused."""
    overlays = read_overlays(OVERLAYS_FILE)
    unknown = sorted({event for overlay in overlays for event in overlay.emit} - set(osc.EVENTS))
    if unknown:
        raise ExtensionError(f'{OVERLAYS_FILE.name}: unknown event(s) {unknown}; known: {sorted(osc.EVENTS)}')
    return Extension(overlays=overlays, notify=osc.nudge, identity=ticket_subject, prompt_vault=False,
                     on_start=sync_at_start)


def sync_at_start(dispatch: Callable[[str], int]) -> None:
    """Bring the clone up to date before the first prompt — quietly, unless it did not happen.

    Silence would open the shell on a stale clone with no hint — a diverged branch, a locked
    vault, no network — so a failed sync prints one line naming what to do. After a key
    rotation `git-sync` is the very thing that cannot work and the fix is a message waiting in
    the spool, so that is asked first.
    """
    prev_quiet, console.quiet = console.quiet, True
    try:
        rc = dispatch('git-sync')
    finally:
        console.quiet = prev_quiet
    if rc != 0:
        from solver.core.git import key_waiting_hint
        hint = key_waiting_hint() or ('could not sync with origin/master — this clone may be '
                                      'stale; run [accent]git-sync[/accent] to see why.')
        console.print(f'[warning]{hint}[/warning]')

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

Both extensions here add the host's own commands — `msg`, `users` and key distribution
(:mod:`solver.web.shell.keys`) — and carry the solver shell's notices on the message spool
(:mod:`solver.web.shell.notices`). :func:`host_extension` is the same minus the browser: the
OS login, a terminal vault prompt, no OSC; `solver-host` runs it, for the operator's terminal
on the web host.
"""
from __future__ import annotations

__all__ = ['HOST_COMMANDS', 'HOST_OVERLAYS_FILE', 'OVERLAYS_FILE', 'extension', 'host_extension', 'host_main',
           'sync_at_start']

from pathlib import Path
from typing import Callable

from solver.shell.extension import Extension, ExtensionError, read_overlays
from solver.shell.tty import console
from solver.web.shell import osc
from solver.web.shell.identity import ticket_subject
from solver.web.shell.notices import HOST_KEY_HINT, WEB_KEY_HINT, Spool

#: The overlay tables, shipped as package data: the web shell's, and the host terminal's.
OVERLAYS_FILE: Path = Path(__file__).with_name('overlays.toml')
HOST_OVERLAYS_FILE: Path = Path(__file__).with_name('host.toml')
#: The command modules only the web host can run: they need its spool, roster and mail relay.
HOST_COMMANDS: tuple[str, ...] = ('solver.web.auth.commands', 'solver.web.msg.commands', 'solver.web.shell.keys')


def extension() -> Extension:
    """The web shell's extension; an overlay emitting an event :mod:`osc` cannot send is refused."""
    overlays = read_overlays(OVERLAYS_FILE)
    unknown = sorted({event for overlay in overlays for event in overlay.emit} - set(osc.EVENTS))
    if unknown:
        raise ExtensionError(f'{OVERLAYS_FILE.name}: unknown event(s) {unknown}; known: {sorted(osc.EVENTS)}')
    return Extension(modules=HOST_COMMANDS, overlays=overlays, notify=osc.nudge, identity=ticket_subject,
                     prompt_vault=False, on_start=sync_at_start, notices=Spool(WEB_KEY_HINT))


def host_extension() -> Extension:
    """The host terminal's extension: the host's commands and the spool, nothing of the browser."""
    return Extension(modules=HOST_COMMANDS, overlays=read_overlays(HOST_OVERLAYS_FILE),
                     notices=Spool(HOST_KEY_HINT))


def host_main() -> int:  # pragma: no cover — the `solver-host` console script
    """`solver-host`: the solver shell with the web host's commands, in a terminal."""
    from solver.main import main
    try:
        ext = host_extension()
    except ExtensionError as exc:
        raise SystemExit(f'extension: {exc} — refusing to start') from None
    return main(extension=ext)


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

#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The web shell: the solver shell, extended for a PTY framed by the browser.

The solver shell runs standalone and knows nothing of the web. This package composes it with
an :class:`~solver.shell.extension.Extension` (docs/package-split.md § 3.2): the overlay table
`overlays.toml` makes the state-changing commands nudge the page over `OSC 5379`
(:mod:`solver.web.shell.osc`) and replaces `show` / `edit` with bodies that swap the app
shell's left pane (:mod:`solver.web.shell.viewer`). The PTY runs `python -m solver.web.shell`.
"""
from __future__ import annotations

__all__ = ['OVERLAYS_FILE', 'extension']

from pathlib import Path

from solver.shell.extension import Extension, ExtensionError, read_overlays
from solver.web.shell import osc

#: The overlay table, shipped as package data.
OVERLAYS_FILE: Path = Path(__file__).with_name('overlays.toml')


def extension() -> Extension:
    """The web shell's extension; an overlay emitting an event :mod:`osc` cannot send is refused."""
    overlays = read_overlays(OVERLAYS_FILE)
    unknown = sorted({event for overlay in overlays for event in overlay.emit} - set(osc.EVENTS))
    if unknown:
        raise ExtensionError(f'{OVERLAYS_FILE.name}: unknown event(s) {unknown}; known: {sorted(osc.EVENTS)}')
    return Extension(overlays=overlays, notify=osc.nudge)

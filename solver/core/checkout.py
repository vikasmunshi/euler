#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Workspace checkout marker: a presence-based guard that blocks `reset`.

The checkout marker (`config.checkout`) is a plain presence file. While it exists `reset` refuses to
clear the workspace and a `checkin` must remove it first. Unlike the `fcntl` workspace/instance locks in
`solver.core.lock`, the marker is presence/content based rather than tied to a live PID — so a marker set
by an in-flight `claude-api` / `claude-skill` run is visible to, and blocks, an accidental `reset` from
the browser viewer or a sibling shell, none of which share the writer's PID. The trade-off: a crash leaves
a stale marker that only an explicit `checkin` clears (there is deliberately no force-reset override).

Two decorators expose the guard to commands:

* :func:`requires_checkin` — refuse to run while checked out (applied to `reset`); carries the `⊘` glyph.
* :func:`auto_checkout`    — check out for the command's duration (applied to `claude-api` /
  `claude-skill`); carries the `⚑` glyph.
"""
from __future__ import annotations

__all__ = ['auto_checkout', 'clear_workspace_checkout', 'requires_checkin', 'set_workspace_checkout',
           'workspace_checkout_reason', 'checkout', 'checkin']

import functools
from datetime import datetime
from typing import Callable

from solver.config import ExitCodes, config
from solver.core.lock import check_workspace_lock_command
from solver.shell import console, register


def workspace_checkout_reason() -> str | None:
    """Return the checkout reason if the workspace is checked out, else None."""
    try:
        return config.checkout.read_text(encoding='utf-8').strip() or '(no reason given)'
    except OSError:
        return None


def set_workspace_checkout(reason: str) -> None:
    """Create (or update) the workspace checkout marker with a human-readable `reason`."""
    config.checkout.parent.mkdir(parents=True, exist_ok=True)
    config.checkout.write_text(reason, encoding='utf-8')


def clear_workspace_checkout() -> None:
    """Remove the workspace checkout marker if present (a no-op when not checked out)."""
    config.checkout.unlink(missing_ok=True)


def auto_checkout[**P](func: Callable[P, int], *, reason: str | None = None) -> Callable[P, int]:
    """Decorator: check the workspace out for the duration of the command.

    On entry sets the checkout marker *only* when the workspace is not already checked out, and clears
    it on exit *only* in that case — so an outer manual `checkout` is never clobbered. Applied to
    `claude-api` / `claude-skill` (and the in-shell `! claude`) to fence their workspace mutations
    against a stray `reset` (e.g. the web viewer button) while they run.

    The marker `reason` defaults to the wrapped command's name; pass an explicit `reason` when the
    callable's name is not what should be shown (e.g. wrapping a generic runner for `! claude`).
    """
    mark = reason or func.__name__.replace('_', '-')

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> int:
        created = workspace_checkout_reason() is None
        if created:
            set_workspace_checkout(mark)
        try:
            return func(*args, **kwargs)
        finally:
            if created:
                clear_workspace_checkout()

    wrapper.__auto_checkout__ = True  # type: ignore[attr-defined]
    return wrapper


def requires_checkin[**P](func: Callable[P, int]) -> Callable[P, int]:
    """Decorator: refuse to run the command while the workspace is checked out.

    If the checkout marker is present, prints an error naming the checkout reason and returns
    `EXIT_ERROR` without calling the wrapped command; otherwise runs it unchanged. Applied to `reset`
    so an in-progress checkout (manual or from an AI run) cannot be cleared until an explicit `checkin`.
    """
    from solver.shell import console

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> int:
        if (reason := workspace_checkout_reason()) is not None:
            console.print(f'[error]error:[/error] workspace is checked out ([accent]{reason}[/accent]); '
                          f'run [accent]checkin[/accent] first')
            return ExitCodes.EXIT_ERROR
        return func(*args, **kwargs)

    wrapper.__requires_checkin__ = True  # type: ignore[attr-defined]
    return wrapper


@register(help_text='Check out the workspace, blocking `init` and `reset` until checkin.', quietable=True)
@check_workspace_lock_command
def checkout(reason: str = '') -> int:
    """Mark the workspace checked out so `init`/`reset` refuses until a `checkin`.

    Protects an in-progress workspace from an accidental `reset` — including the reset button on the
    web viewer and a sibling shell — by leaving a presence marker that any process can see. `claude-api`
    and `claude-skill` check out automatically while they run; this is the manual equivalent. The marker
    persists until `checkin` (there is no force-reset), so it also survives a crash until cleared.

    Args:
        reason: Free-text note recorded in the marker and echoed when a reset is refused.
    """
    if (current := workspace_checkout_reason()) is not None:
        console.print(f'[warning]Workspace is already checked out ([accent]{current}[/accent]).[/warning]')
        return ExitCodes.EXIT_OK
    set_workspace_checkout(reason or f'checked out {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}')
    console.print('[success]Workspace checked out[/success] — '
                  '[muted]run [accent]checkin[/accent] to release.[/muted]')
    return ExitCodes.EXIT_OK


@register(help_text='Check in the workspace, re-allowing `init` and `reset`.', quietable=True)
@check_workspace_lock_command
def checkin() -> int:
    """Clear the checkout marker left by `checkout`, re-allowing `init` and `reset`."""
    if workspace_checkout_reason() is None:
        console.print('[muted]Workspace is not checked out.[/muted]')
        return ExitCodes.EXIT_OK
    clear_workspace_checkout()
    console.print('[success]Workspace checked in.[/success]')
    return ExitCodes.EXIT_OK

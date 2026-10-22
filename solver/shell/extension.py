#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Extensions: how a package built on the solver shell adds to it, without the shell knowing.

docs/package-split.md § 3.2. The solver shell runs standalone; a package that extends it —
the web shell — hands :func:`solver.main.main` an :class:`Extension` instead of being
discovered. Composition is explicit on purpose: plugin discovery (`entry_points`) would load
an extension into *every* shell of a venv it is installed in, the terminal one included.

An extension may bring its own **identity** (who the session runs as, in place of the OS
login), say whether the vault may be unlocked by prompting, and run a step before the first
prompt. It contributes extra command modules and an **overlay table**, one overlay per
command it changes:

- `emit` — events passed to the extension's `notify` after the command returns, whatever its
  exit code (a failed command may still have changed state, and every event is meant as an
  idempotent "re-read" nudge). The shell attaches no meaning to the event names.
- `replace` — a `module:attr` reference to a function that runs in place of the command's
  own. It must have the same signature (:func:`~solver.shell.register.replace_body`).

The table is TOML, keyed by command name::

    [git-pull]
    emit = ["git"]

    [show]
    replace = "euler_webshell.viewer:show"

An overlay that names no command, or a replacement that does not fit, is an
:class:`ExtensionError` — the shell refuses to start rather than run with the two sides out of
step. A command the subject is below the floor of is *withheld*, not unknown: its overlay is
skipped.
"""
from __future__ import annotations

__all__ = ['Extension', 'ExtensionError', 'Overlay', 'apply_overlays', 'check_overlays', 'load_extension',
           'read_overlays']

import importlib
import tomllib
from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from typing import Any, Callable

from solver.auth import Subject
from solver.shell.command import Command, CommandFn, CommandRegistry, Context, registry
from solver.shell.register import check_replacement, replace_body

#: The keys an overlay may carry.
_OVERLAY_KEYS: frozenset[str] = frozenset({'emit', 'replace'})


class ExtensionError(Exception):
    """An extension does not fit the shell it extends."""


@dataclass(frozen=True)
class Overlay:
    """One command's changes: events to emit after it, and/or a replacement body."""
    command: str
    emit: tuple[str, ...] = ()
    replace: str = ''


@dataclass(frozen=True)
class Extension:
    """What an extending package hands :func:`solver.main.main`."""
    #: Command modules to import after the shell's own.
    modules: tuple[str, ...] = ()
    overlays: tuple[Overlay, ...] = ()
    #: Receives each `emit` event; required when any overlay emits.
    notify: Callable[[str], None] | None = None
    #: Who the shell runs as, in place of the OS login (:mod:`solver.shell.login`). Called once,
    #: before any command module loads; raises :class:`SystemExit` to refuse the session.
    identity: Callable[[], Subject] | None = None
    #: Whether a locked vault may be unlocked by asking at the terminal. A front end that
    #: unlocks it some other way (the web shell: the browser) says no.
    prompt_vault: bool = True
    #: Runs once before the first interactive prompt, given the shell's `dispatch`.
    on_start: Callable[[Callable[[str], int]], None] | None = None


def read_overlays(path: Path) -> tuple[Overlay, ...]:
    """Parse an overlay table (TOML, one table per command name)."""
    try:
        data: dict[str, Any] = tomllib.loads(path.read_text(encoding='utf-8'))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ExtensionError(f'{path}: {exc}') from None
    overlays: list[Overlay] = []
    for name, entry in data.items():
        if not isinstance(entry, dict) or not entry or set(entry) - _OVERLAY_KEYS:
            raise ExtensionError(f'{path}: [{name}] takes only {sorted(_OVERLAY_KEYS)}')
        emit, replace = entry.get('emit', []), entry.get('replace', '')
        if not isinstance(emit, list) or not all(isinstance(e, str) and e for e in emit):
            raise ExtensionError(f'{path}: [{name}] emit must be a list of event names')
        if not isinstance(replace, str) or (replace and ':' not in replace):
            raise ExtensionError(f'{path}: [{name}] replace must be "module:attr"')
        overlays.append(Overlay(command=name, emit=tuple(emit), replace=replace))
    return tuple(overlays)


def _resolve(ref: str) -> Callable[..., int]:
    """Import the function a `module:attr` reference names."""
    module, _, attr = ref.partition(':')
    try:
        func = getattr(importlib.import_module(module), attr)
    except (ImportError, AttributeError) as exc:
        raise ExtensionError(f'replace {ref!r}: {exc}') from None
    if not callable(func):
        raise ExtensionError(f'replace {ref!r}: not callable')
    return func  # type: ignore[no-any-return]


def _emitting(func: CommandFn, events: tuple[str, ...], notify: Callable[[str], None]) -> CommandFn:
    """Wrap a registered command so *events* reach *notify* once it returns."""

    @wraps(func)
    def _after(ctx: Context, *args: str) -> int:
        try:
            return func(ctx, *args)
        finally:
            for event in events:
                notify(event)

    return _after


def _applicable(extension: Extension, commands: CommandRegistry) -> list[tuple[Overlay, Command]]:
    """Every overlay of *extension* paired with its registered command, all checked first.

    Raises :class:`ExtensionError` on the first overlay that does not fit, changing nothing;
    an overlay on a withheld command is left out.
    """
    applicable: list[tuple[Overlay, Command]] = []
    for overlay in extension.overlays:
        cmd = commands.resolve(overlay.command)
        if cmd is None or cmd.name != overlay.command:
            if overlay.command in commands.withheld:
                continue
            raise ExtensionError(f'overlay names no command {overlay.command!r}'
                                 + (f' (an alias of {cmd.name!r})' if cmd else ''))
        if overlay.replace:
            try:
                check_replacement(cmd.name, _resolve(overlay.replace))
            except ValueError as exc:
                raise ExtensionError(str(exc)) from None
        if overlay.emit and extension.notify is None:
            raise ExtensionError(f'overlay {overlay.command!r} emits, but the extension has no notify')
        applicable.append((overlay, cmd))
    return applicable


def check_overlays(extension: Extension, commands: CommandRegistry = registry) -> None:
    """Raise :class:`ExtensionError` unless every overlay fits *commands*; changes nothing."""
    _applicable(extension, commands)


def apply_overlays(extension: Extension, commands: CommandRegistry = registry) -> None:
    """Apply *extension*'s overlays to the registered commands — all of them, or (on a misfit) none."""
    for overlay, cmd in _applicable(extension, commands):
        if overlay.replace:
            replace_body(cmd.name, _resolve(overlay.replace))
        if overlay.emit:
            assert extension.notify is not None  # checked by _applicable
            cmd.func = _emitting(cmd.func, overlay.emit, extension.notify)


def load_extension(extension: Extension, commands: CommandRegistry = registry) -> None:
    """Import *extension*'s command modules, then apply its overlays."""
    for module in extension.modules:
        try:
            importlib.import_module(module)
        except ImportError as exc:
            raise ExtensionError(f'module {module!r}: {exc}') from None
    apply_overlays(extension, commands)

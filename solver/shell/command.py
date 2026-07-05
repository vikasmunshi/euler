#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Command framework for shell v2: Context, Command, registry, and decorator.

Self-contained (no dependency on the v1 shell). A command is a plain function
taking a :class:`Context` (exposing the shared console and the variable store)
followed by its parsed argv tokens, and returning an `int` exit code.
"""
from __future__ import annotations

__all__ = ['Command', 'CommandRegistry', 'Context', 'command', 'is_authorized', 'is_authorized_for',
           'registry']

import csv
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Callable, Iterable

from prompt_toolkit.completion import Completion
from rich.console import Console

from solver.config import config
from solver.shell.tty import console
from solver.shell.variables import Variables, variables

#: Column values read as "granted" in the command-authorization CSV.
_TRUTHY: frozenset[str] = frozenset({'true', '1', 'yes'})


@lru_cache(maxsize=1)
def _authorization_policy() -> dict[str, frozenset[str]]:
    """Map ``command name → the profiles allowed to use it``, from ``config.commands_file``.

    The CSV (``solver/commands.csv``) mirrors ``modules.csv``: a header ``command``
    then one boolean column per profile (``admin``/``user``/``guest``), a truthy cell
    granting that profile the command. A missing or unreadable file yields an empty
    policy — every command then falls back to admin-only (see :func:`is_authorized`).
    Cached: the policy is fixed for a process (one shell serves one identity).
    """
    try:
        rows = list(csv.DictReader(config.commands_file.read_text(encoding='utf-8').splitlines()))
    except OSError:
        return {}
    profiles = ('admin', 'user', 'guest')
    policy: dict[str, frozenset[str]] = {}
    for row in rows:
        name = (row.get('command') or '').strip()
        if name:
            policy[name] = frozenset(p for p in profiles if (row.get(p) or '').strip().lower() in _TRUTHY)
    return policy


def is_authorized_for(cmd_name: str, profile: str) -> bool:
    """True if *profile* may use *cmd_name* under the ``commands.csv`` policy.

    A command listed in the policy is allowed only for the profiles its row grants; a
    command **absent** from the policy is admin-only, so a newly added command is never
    silently exposed to ``user``/``guest`` until it is added to ``commands.csv``. Takes
    the profile explicitly so a caller (e.g. the web tier, running as one process for
    many users) can check on behalf of an identity other than its own.
    """
    allowed = _authorization_policy().get(cmd_name)
    if allowed is None:
        return profile == 'admin'
    return profile in allowed


def is_authorized(cmd_name: str) -> bool:
    """True if the current process's profile (``config.user_profile``) may use *cmd_name*."""
    return is_authorized_for(cmd_name, config.user_profile)


@dataclass
class Context:
    """Runtime context passed to every command as its first argument.

    Exposes the shared :class:`rich.console.Console` and the variable store, plus
    the parsed argv and raw line. `shell` is the owning shell (loosely typed to
    avoid a framework→shell dependency); commands rarely need it.
    """
    shell: Any = None
    console: Console = console
    variables: Variables = variables
    raw_line: str = ''
    argv: list[str] = field(default_factory=list)
    block: Any = None


#: Signature of a command callable; extra args come from the parsed input line.
CommandFn = Callable[..., int]


@dataclass
class Command:
    """A registered shell command, keyed by name (and optional aliases)."""
    name: str
    func: CommandFn
    help: str = ''
    usage: str = ''
    aliases: tuple[str, ...] = ()
    completer: Callable[[Context, str], Iterable[str | Completion]] | None = None

    def invoke(self, ctx: Context) -> int:
        """Call the command's function with *ctx* and the parsed argv, returning its exit code."""
        return self.func(ctx, *ctx.argv)


class CommandRegistry():
    """Registry of :class:`Command` instances, keyed by name and alias."""

    def __init__(self) -> None:
        self._commands: dict[str, Command] = {}
        self._by_alias: dict[str, str] = {}

    def register(self, cmd: Command) -> Command:
        """Register *cmd*; raises :class:`ValueError` on name/alias conflict."""
        if cmd.name in self._commands or cmd.name in self._by_alias:
            raise ValueError(f'command {cmd.name!r} is already registered')
        self._commands[cmd.name] = cmd
        for alias in cmd.aliases:
            if alias in self._commands or alias in self._by_alias:
                raise ValueError(f'alias {alias!r} conflicts with existing command')
            self._by_alias[alias] = cmd.name
        return cmd

    def unregister(self, name: str) -> None:
        """Remove the command named *name* and its aliases; a no-op if it is absent."""
        cmd = self._commands.pop(name, None)
        if cmd is None:
            return
        for alias in cmd.aliases:
            self._by_alias.pop(alias, None)

    def resolve(self, token: str) -> Command | None:
        """Return the command registered under *token* (a name or alias), or None."""
        if token in self._commands:
            return self._commands[token]
        target = self._by_alias.get(token)
        return self._commands.get(target) if target else None

    def names(self, include_aliases: bool = True) -> list[str]:
        """Return all registered command names, sorted, optionally including aliases."""
        out = list(self._commands)
        if include_aliases:
            out.extend(self._by_alias)
        return sorted(out)

    def all(self) -> list[Command]:
        """Return every registered command, sorted by name (aliases excluded)."""
        return sorted(self._commands.values(), key=lambda c: c.name)


#: Default, module-level registry used by the :func:`command` decorator.
registry = CommandRegistry()


def command(
        name: str | None = None,
        *,
        help_text: str = '',
        usage: str = '',
        aliases: tuple[str, ...] = (),
        completer: Callable[[Context, str], Iterable[str | Completion]] | None = None,
) -> Callable[[CommandFn], CommandFn]:
    """Decorator that registers *func* as a shell command (returned unchanged)."""

    def _decorate(func: CommandFn) -> CommandFn:
        cmd_name = name or func.__name__.lstrip('_').replace('_', '-')
        if not is_authorized(cmd_name):
            # Not permitted for this shell's profile → leave it unregistered (invisible to
            # help/completion, "unknown command" if invoked). The function is returned
            # unchanged so it still works as a plain Python callable.
            return func
        cmd_help = help_text
        if not cmd_help and func.__doc__:
            cmd_help = func.__doc__.strip().splitlines()[0]
        registry.register(Command(
            name=cmd_name,
            func=func,
            help=cmd_help,
            usage=usage,
            aliases=tuple(aliases),
            completer=completer,
        ))
        return func

    return _decorate

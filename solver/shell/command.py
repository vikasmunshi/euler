#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Command framework for shell v2: Context, Command, registry, and decorator.

Self-contained (no dependency on the v1 shell). A command is a plain function
taking a :class:`Context` (exposing the shared console and the variable store)
followed by its parsed argv tokens, and returning an `int` exit code.
"""
from __future__ import annotations

__all__ = ['Command', 'CommandRegistry', 'Context', 'command', 'effective_requires',
           'is_permitted', 'registry']

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable

from prompt_toolkit.completion import Completion
from rich.console import Console

from solver.auth import FAILCLOSED_PERMISSION
from solver.config import config
from solver.shell.tty import console
from solver.shell.variables import Variables, variables


def effective_requires(requires: tuple[str, ...]) -> tuple[str, ...]:
    """Normalise a command's ``requires`` — an empty list is **fail-closed** to
    ``infra:execute`` (admin-only), so a command that declares nothing is never
    silently exposed (DD-12)."""
    return requires or (FAILCLOSED_PERMISSION,)


def is_permitted(requires: tuple[str, ...], channels: tuple[str, ...]) -> bool:
    """True if the current process's :class:`~solver.auth.Subject` may run a command
    with these *requires* / *channels* — i.e. its channel is allowed **and** it holds
    every required ``object:permission`` (DD-12). One process serves one subject."""
    subject = config.subject
    return subject.channel in channels and subject.has_all(effective_requires(requires))


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
    #: The ``object:permission`` grants this command needs (DD-12). Empty ⇒ the
    #: fail-closed default (admin-only); stored expanded so it is never empty.
    requires: tuple[str, ...] = ()
    #: The channels this command is valid in (``terminal``/``web``).
    channels: tuple[str, ...] = ('terminal', 'web')

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
        requires: tuple[str, ...] = (),
        channels: tuple[str, ...] = ('terminal', 'web'),
) -> Callable[[CommandFn], CommandFn]:
    """Decorator that registers *func* as a shell command (returned unchanged).

    ``requires`` is the ``object:permission`` grants the command needs and
    ``channels`` the channels it is valid in (DD-12); an empty ``requires`` is
    fail-closed to admin-only. The command registers only if the current subject's
    channel is allowed and it holds every required permission — otherwise it is
    left unregistered (invisible to help/completion, "unknown command" if invoked),
    while the function is returned unchanged so it stays a plain Python callable.
    """

    def _decorate(func: CommandFn) -> CommandFn:
        cmd_name = name or func.__name__.lstrip('_').replace('_', '-')
        if not is_permitted(requires, channels):
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
            requires=effective_requires(requires),
            channels=tuple(channels),
        ))
        return func

    return _decorate

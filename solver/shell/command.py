#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Command framework for shell v2: Context, Command, registry, and decorator.

Self-contained (no dependency on the v1 shell). A command is a plain function
taking a :class:`Context` (exposing the shared console and the variable store)
followed by its parsed argv tokens, and returning an `int` exit code.
"""
from __future__ import annotations

__all__ = ['Command', 'CommandRegistry', 'Context', 'command', 'registry']

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable

from prompt_toolkit.completion import Completion
from rich.console import Console

from solver.config import Singleton
from solver.shell.tty import console
from solver.shell.variables import Variables, variables


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
        return self.func(ctx, *ctx.argv)


class CommandRegistry(metaclass=Singleton):
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
        cmd = self._commands.pop(name, None)
        if cmd is None:
            return
        for alias in cmd.aliases:
            self._by_alias.pop(alias, None)

    def resolve(self, token: str) -> Command | None:
        if token in self._commands:
            return self._commands[token]
        target = self._by_alias.get(token)
        return self._commands.get(target) if target else None

    def names(self, include_aliases: bool = True) -> list[str]:
        out = list(self._commands)
        if include_aliases:
            out.extend(self._by_alias)
        return sorted(out)

    def all(self) -> list[Command]:
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

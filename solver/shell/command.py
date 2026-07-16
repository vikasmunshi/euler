#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Command framework for shell v2: Context, Command, registry, and decorator.

Self-contained (no dependency on the v1 shell). A command is a plain function
taking a :class:`Context` (exposing the shared console and the variable store)
followed by its parsed argv tokens, and returning an `int` exit code.
"""
from __future__ import annotations

__all__ = ['Command', 'CommandRegistry', 'Context', 'command', 'is_permitted', 'registry']

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Literal

from prompt_toolkit.completion import Completion
from rich.console import Console

from solver.config import config
from solver.shell.tty import console
from solver.shell.variables import Variables, variables


def is_permitted(requires: str) -> bool:
    """True if the current process's :class:`~solver.auth.Subject` may run a command whose
    minimum profile is *requires* — a plain ladder-rank comparison. Every command must
    declare its floor, so there is nothing to default. Authorization is by profile only;
    the channel (terminal vs web) is **not** an authorization axis — a user's web shell is
    bash in their own per-user sandbox, no different from their terminal. One process
    serves one subject."""
    return config.subject.has(requires)


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
    #: The minimum profile this command needs. Mandatory on the decorator, so a
    #: command can never be silently exposed by omitting its floor.
    requires: str = ''

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
        requires: Literal['reader', 'contributor', 'maintainer', 'admin'],
) -> Callable[[CommandFn], CommandFn]:
    """Decorator that registers *func* as a shell command (returned unchanged).

    ``requires`` is the **minimum profile** the command needs
    (``'reader'``/``'contributor'``/``'maintainer'``/``'admin'``) and is **mandatory**:
    omitting it is a type error, so a command can never be exposed by forgetting to
    declare its floor. The command registers only if the current subject's profile is at
    or above that floor — otherwise it is left unregistered (invisible to help/completion,
    "unknown command" if invoked), while the function is returned unchanged so it stays a
    plain Python callable. Authorization is by profile only; the channel is not an axis.
    """

    def _decorate(func: CommandFn) -> CommandFn:
        cmd_name = name or func.__name__.lstrip('_').replace('_', '-')
        if not is_permitted(requires):
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
            requires=requires,
        ))
        return func

    return _decorate

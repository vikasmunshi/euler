#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Experimental interactive shell built on prompt-toolkit and rich.

This module provides an alternative to :mod:`solver.core.cli` (which is based
on :mod:`cmd`).  It does **not** port the existing commands; instead it
offers a small, pluggable framework so that commands can be registered from
anywhere in the codebase via a decorator or by subclassing :class:`Command`.

Design goals
------------
* Look and feel inspired by the Junie UI: a soft, modern terminal aesthetic
  with rounded panels, subtle colors, a left-side accent bar, and a compact
  status footer.
* Strict separation between *framework* (this file) and *commands* (to be
  added in sibling modules).
* Async-friendly prompt loop powered by 'prompt_toolkit.PromptSession' with
  history, auto-suggest, completion and key bindings.
* Rich-rendered output via a shared :class:`rich.console.Console`.
"""
from __future__ import annotations

import os
import shlex
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme

from solver.core.config import config

# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------

#: Rich theme used for all output.
#: (warm accent on a near-black surface, muted secondary text).
SOLVER_THEME = Theme({
    'accent': 'bold #f97316',  # warm orange accent (Junie highlight)
    'accent.dim': '#c2410c',
    'primary': '#e5e7eb',  # near-white body text
    'muted': '#9ca3af',  # secondary / hints
    'success': 'bold #22c55e',
    'warning': 'bold #f59e0b',
    'error': 'bold #ef4444',
    'panel.border': '#3f3f46',
    'prompt.path': '#60a5fa',
    'prompt.symbol': 'bold #f97316',
    'cmd.name': 'bold #fbbf24',
    'cmd.help': '#9ca3af',
})

#: prompt-toolkit style for the input line.
PT_STYLE = Style.from_dict({
    'prompt.bar': '#f97316 bold',
    'prompt.path': '#60a5fa',
    'prompt.symbol': '#f97316 bold',
    'prompt.user': '#e5e7eb',
    '': '#e5e7eb',  # default input text
    'bottom-toolbar': 'bg:#27272a #9ca3af',
})

#: Shared console instance; used by the shell and importable by command modules.
console: Console = Console(theme=SOLVER_THEME, highlight=False)


# ---------------------------------------------------------------------------
# Command framework
# ---------------------------------------------------------------------------

@dataclass
class Context:
    """Runtime context passed to every command invocation.

    Commands receive this as their first argument.  It exposes the shared
    :class:`rich.console.Console` together with the owning shell so commands
    can introspect or mutate shell state (e.g. exit, reload, register new
    commands at runtime).
    """
    shell: 'SolverShell'
    console: Console
    raw_line: str = ''
    argv: list[str] = field(default_factory=list)


#: Signature of a command callable.  Extra positional / keyword arguments are
#: parsed from the user's input line via :func:`shlex.split`.
CommandFn = Callable[..., Optional[bool]]


@dataclass
class Command:
    """A registered shell command.

    Attributes
    ----------
    name:
        Primary command name (the first whitespace-separated token on the
        input line).
    func:
        Callable invoked with a :class:`Context` followed by parsed argv
        tokens.  May return 'True' to request that the shell exit.
    help:
        Short one-line help string, shown in the 'help' listing.
    usage:
        Optional usage signature, shown by 'help <cmd>'.
    aliases:
        Alternative names that resolve to this command.
    completer:
        Optional callable '(ctx, text) -> list[str]' producing argument
        completions for the command.
    """
    name: str
    func: CommandFn
    help: str = ''
    usage: str = ''
    aliases: tuple[str, ...] = ()
    completer: Optional[Callable[[Context, str], Iterable[str | Completion]]] = None

    def invoke(self, ctx: Context) -> Optional[bool]:
        return self.func(ctx, *ctx.argv)


class CommandRegistry:
    """Registry of :class:`Command` instances, keyed by name and alias.

    A module-level :data:`registry` is provided for convenience; you may also
    instantiate private registries for embedded shells.
    """

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

    def resolve(self, token: str) -> Optional[Command]:
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
        name: Optional[str] = None,
        *,
        help: str = '',
        usage: str = '',
        aliases: tuple[str, ...] = (),
        completer: Optional[Callable[[Context, str], Iterable[str | Completion]]] = None,
        registry: CommandRegistry = registry,
) -> Callable[[CommandFn], CommandFn]:
    """Decorator that registers *func* as a shell command.

    Example
    -------
    >>> @command(name='echo', help='Echo arguments.', aliases=('e',))
    ... def _echo(ctx: Context, *args: str) -> None:
    ...     ctx.console.print(' '.join(args))
    """

    def _decorate(func: CommandFn) -> CommandFn:
        cmd_name = name or func.__name__.lstrip('_').replace('_', '-')
        cmd_help = help
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


# ---------------------------------------------------------------------------
# prompt-toolkit glue
# ---------------------------------------------------------------------------

class _ShellCompleter(Completer):
    """Completer that delegates to per-command completers after the first token."""

    def __init__(self, shell: 'SolverShell') -> None:
        self._shell = shell

    def get_completions(self, document: Document, complete_event: Any) -> Iterable[Completion]:
        text_before = document.text_before_cursor
        try:
            tokens = shlex.split(text_before, posix=True)
        except ValueError:
            tokens = text_before.split()
        # First word: complete command names.
        if not tokens or (text_before and not text_before.endswith(' ') and len(tokens) == 1):
            prefix = tokens[0] if tokens else ''
            for name in self._shell.registry.names():
                if name.startswith(prefix):
                    yield Completion(name, start_position=-len(prefix))
            return
        # Subsequent words: delegate to command completer if available.
        head = tokens[0]
        cmd = self._shell.registry.resolve(head)
        if cmd is None or cmd.completer is None:
            return
        partial = '' if text_before.endswith(' ') else tokens[-1]
        ctx = Context(shell=self._shell, console=self._shell.console,
                      raw_line=text_before, argv=tokens[1:])
        for candidate in cmd.completer(ctx, partial):
            if isinstance(candidate, Completion):
                yield candidate
            elif candidate.startswith(partial):
                yield Completion(candidate, start_position=-len(partial))


# ---------------------------------------------------------------------------
# Shell
# ---------------------------------------------------------------------------

@dataclass
class SolverShell:
    """Interactive shell built on prompt-toolkit + rich.

    Parameters
    ----------
    registry:
        Command registry to use.  Defaults to the module-level
        :data:`registry`, so commands declared with :func:`command` are
        picked up automatically.
    history_file:
        Path to a persistent history file (created on first use).
    workspace:
        Free-form label shown in the prompt; typically the current
        workspace path.
    """

    registry: CommandRegistry = field(default_factory=lambda: registry)
    history_file: Path = field(default_factory=lambda: Path.home() / '.solver_history')
    workspace: Path = field(default_factory=lambda: config.workspace_dir)
    console: Console = field(default_factory=lambda: console)

    _running: bool = field(default=False, init=False, repr=False)
    _session: Optional[PromptSession] = field(default=None, init=False, repr=False)

    # -- lifecycle ----------------------------------------------------------

    def run(self, intro: bool = True, commands: Optional[list[str]] = None) -> int:
        """Run the prompt loop until the user exits.  Returns a process exit code.

        Parameters
        ----------
        intro:
            If True, print the welcome banner before entering the loop.
        commands:
            Optional list of commands to execute at startup (e.g. from the
            CLI).  Each entry is dispatched as if typed at the prompt; if any
            command requests exit (e.g. 'exit'), the loop terminates before
            entering interactive mode.
        """
        os.chdir(self.workspace)
        self._session = PromptSession(
            history=FileHistory(str(self.history_file)),
            auto_suggest=AutoSuggestFromHistory(),
            completer=_ShellCompleter(self),
            complete_while_typing=True,
            key_bindings=self._build_keybindings(),
            style=PT_STYLE,
            bottom_toolbar=self._bottom_toolbar,
        )
        if intro:
            self._print_banner()
        self._running = True
        # Replay any startup commands first; abort the interactive loop if one exits.
        for line in commands or []:
            if not line.strip():
                continue
            self.console.print(
                f'[accent]▎[/accent] [primary]{self.workspace.name}[/primary] '
                f'[accent]❯[/accent] {line}'
            )
            try:
                if self.dispatch(line):
                    self._running = False
                    break
            except SystemExit:
                raise
            except Exception as exc:  # noqa: BLE001
                self.console.print(f'[error]error:[/error] {exc}')
        while self._running:
            try:
                line = self._session.prompt(self._build_prompt())
            except KeyboardInterrupt:
                self.console.print('[muted]^C[/muted]')
                continue
            except EOFError:
                break
            if not line.strip():
                continue
            try:
                if self.dispatch(line):
                    break
            except SystemExit:
                raise
            except Exception as exc:  # noqa: BLE001 — top-level UX boundary
                self.console.print(f'[error]error:[/error] {exc}')
        self._print_farewell()
        return 0

    # -- dispatch -----------------------------------------------------------

    def dispatch(self, line: str) -> bool:
        """Parse *line* and dispatch to a registered command.

        Returns 'True' if the shell should exit.
        Lines beginning with a sigil ('!', '?') are rewritten so the
        sigil itself becomes the command name (with the remainder as its
        argument), e.g. '!ls' -> '! ls'.
        """
        stripped = line.lstrip()
        if stripped and stripped[0] in ('!', '?') and (len(stripped) == 1 or stripped[1] != ' '):
            line = f'{stripped[0]} {stripped[1:]}'
        try:
            tokens = shlex.split(line, posix=True)
        except ValueError as exc:
            self.console.print(f'[error]parse error:[/error] {exc}')
            return False
        if not tokens:
            return False
        head, *argv = tokens
        cmd = self.registry.resolve(head)
        if cmd is None:
            self.console.print(f'[error]unknown command:[/error] {head}  '
                               f'[muted](try [accent]help[/accent])[/muted]')
            return False
        ctx = Context(shell=self, console=self.console, raw_line=line, argv=argv)
        return bool(cmd.invoke(ctx))

    def stop(self) -> None:
        """Request the prompt loop to exit after the current iteration."""
        self._running = False

    # -- UI helpers ---------------------------------------------------------

    def _build_prompt(self) -> FormattedText:
        # a vertical accent bar, the workspace path, then a chevron.
        return FormattedText([
            ('class:prompt.bar', '▎'),
            ('class:prompt.path', f' {self.workspace.name} '),
            ('class:prompt.symbol', '❯ '),
        ])

    def _bottom_toolbar(self) -> FormattedText:
        n = len(self.registry.all())
        return FormattedText([
            ('class:bottom-toolbar', f' solver · {n} commands · Ctrl-D to exit '),
        ])

    def _build_keybindings(self) -> KeyBindings:
        kb = KeyBindings()

        @kb.add('c-l')
        def _(event: Any) -> None:
            event.app.renderer.clear()

        return kb

    _LOGO: str = (
        'SOLVER\n'
    )

    def _print_banner(self) -> None:
        # a big accent-colored wordmark, a soft tagline,
        # and a compact "tips" footer — all wrapped in a rounded panel with
        # a left-side accent bar in the title.
        logo = Text(self._LOGO, style='accent', no_wrap=True)
        tagline = Text.assemble(
            ('  Your Euler problem solving companion in the terminal.\n  ', 'primary'),
            ('Powered by ', 'muted'),
            ('prompt-toolkit', 'accent.dim'),
            (' · ', 'muted'),
            ('rich', 'accent.dim'),
            ('.\n\n  ', 'muted'),
            ('  ', ''),
            ('?', 'accent'), (' help   ', 'muted'),
            ('!', 'accent'), (' bash', 'muted'),

        )
        body = Text('\n').join([logo, tagline])
        self.console.print(Panel(
            body,
            border_style='panel.border',
            title='[accent]▎[/accent] [primary]solver[/primary]',
            subtitle='[muted]type [/muted][accent]exit[/accent][muted] '
                     'or press [/muted][accent]Ctrl-D[/accent][muted] to quit[/muted]',
            title_align='left',
            subtitle_align='right',
            padding=(1, 2),
        ))

    def _print_farewell(self) -> None:
        self.console.print('[muted]session ended.[/muted]')


__all__ = (
    'Context',
    'SolverShell',
    'command',
    'console',
)

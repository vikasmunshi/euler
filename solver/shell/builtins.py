#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Built-in framework commands for shell v2: echo, clear, help.

`break` / `continue` / `exit` and `loop` are handled by the language itself
(lexer + interpreter), so they are not registered here.
"""
from __future__ import annotations

__all__ = []

from typing import Iterable

from prompt_toolkit.completion import Completion
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from solver.config import ExitCodes
from solver.shell.command import Context, command


# ------------------------------------------------------- echo ------------------------------------------------------- #
@command(name='echo', help_text='Print text.', usage='\techo <text>')
def _echo(ctx: Context, *args: str) -> int:
    """Print the given text to the console, then succeed.

    The arguments are joined with single spaces and printed literally (no rich
    markup interpretation). Handy in command blocks to annotate progress or to
    surface a variable, since `{...}` references are substituted before the
    command runs — e.g. `echo solved {len(solved)} problems`.
    """
    ctx.console.print(' '.join(args), markup=False)
    return ExitCodes.EXIT_OK


# ------------------------------------------------------- clear ------------------------------------------------------ #
@command(name='clear', help_text='Clear the screen.', usage='\tclear', aliases=('cls',))
def _clear(ctx: Context, *_: str) -> int:
    """Clear the terminal screen and scrollback, then succeed.

    A convenience wrapper over the console's clear; equivalent to the shell
    `clear`. Takes no arguments. Aliased as `cls`.
    """
    ctx.console.clear()
    return ExitCodes.EXIT_OK


# ------------------------------------------------------- help ------------------------------------------------------- #
def _help_completer(ctx: Context, incomplete: str) -> Iterable[str | Completion]:
    """Suggest registered command names (including aliases) for `help`'s argument.

    Only the first positional slot is completed — `help` accepts a single
    optional command name.
    """
    pos_count = len(ctx.argv) - (1 if incomplete else 0)
    if pos_count > 0:
        return []
    return [name for name in ctx.shell.registry.names() if name.startswith(incomplete)]


@command(name='?',
         help_text='List commands or show help for a specific command.',
         usage='\t? [command]',
         aliases=('help',),
         completer=_help_completer)
def _help(ctx: Context, *args: str) -> int:
    """List every command, or show detailed help for one command.

    With no argument, prints a table of all registered commands with their
    aliases and one-line descriptions, plus the legend (§ requires the workspace
    lock, ↻ may refresh workspace state, ⊘ refuses while checked out, ⚑ checks
    out while it runs, » supports --silent).

    With a command name or alias, prints a panel for just that command: its
    description (with the legend glyphs expanded to full sentences), its aliases,
    and its usage. Returns non-zero if the named command is unknown.

    Aliased as `help`.
    """
    reg = ctx.shell.registry
    if args:
        cmd = reg.resolve(args[0])
        if cmd is None:
            ctx.console.print(f'[error]unknown command:[/error] {args[0]}')
            return ExitCodes.EXIT_NOTFOUND
        body = Text()
        help_text = cmd.help or '(no description)'
        help_text = help_text.replace(
            ' [warning]»[/warning]', '\n[warning]»[/warning] supports --silent to suppress output.')
        body.append_text(Text.from_markup(help_text, style='accent.dim'))
        if cmd.aliases:
            body.append('\n\naliases: ', style='muted')
            body.append(', '.join(cmd.aliases), style='accent.dim')
        if cmd.usage:
            body.append('\n\nusage: ', style='muted')
            body.append(cmd.usage, style='accent.dim')
        ctx.console.print(Panel(body, border_style='panel.border',
                                title=f'[accent]▎[/accent] [cmd.name]{cmd.name}[/cmd.name]',
                                title_align='left', padding=(1, 2)))
        return ExitCodes.EXIT_OK
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style='cmd.name', no_wrap=True)
    table.add_column(style='cmd.help')
    for cmd in reg.all():
        names = Text(cmd.name, style='cmd.name')
        if cmd.aliases:
            names.append(f' {" ".join(cmd.aliases)}', style='cmd.help')
        table.add_row(names, cmd.help or '')
    ctx.console.print(Panel(table, border_style='panel.border',
                            title='[accent]▎[/accent] [primary]commands[/primary]',
                            subtitle='[warning]» supports --silent.[/warning]',
                            subtitle_align='right',
                            title_align='left', padding=(1, 2)))
    return ExitCodes.EXIT_OK

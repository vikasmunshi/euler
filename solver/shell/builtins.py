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
@command(requires='reader', name='echo', help_text='Print text.', usage='\techo <text>')
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
@command(requires='reader', name='clear', help_text='Clear the screen.', usage='\tclear', aliases=('cls',))
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


@command(requires='reader', name='?',
         help_text='List commands or show help for a specific command.',
         usage='\t? [command]',
         aliases=('help',),
         completer=_help_completer)
def _help(ctx: Context, *args: str) -> int:
    """List every command, or show detailed help for one command.

    With no argument, prints a three-column table (command, aliases,
    description) of all registered commands; the `»` glyph in a description marks
    a command that supports --silent, as noted in the panel subtitle.

    With a command name or alias, prints a panel for just that command: its
    description (with a trailing `»` glyph expanded to a full sentence about
    --silent), its aliases, and its usage. Returns non-zero if the named command
    is unknown.

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
        help_text = help_text.replace(' [warning]❏[/warning]',
                                      '\n[warning]❏[/warning] uses/sets current problem.')
        help_text = help_text.replace(' [warning]»[/warning]',
                                      '\n[warning]»[/warning] supports --silent to suppress output.')
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
    table = Table(show_header=True, header_style='muted', box=None, padding=(0, 2))
    table.add_column('command', style='accent.dim', no_wrap=True)
    table.add_column('aliases', style='accent.dim', no_wrap=True)
    table.add_column('description', style='cmd.help')
    for cmd in reg.all():
        table.add_row(cmd.name, ' '.join(cmd.aliases), cmd.help or '')
    ctx.console.print(Panel(table,
                            border_style='panel.border',
                            title='[accent]▎[/accent] [primary]commands[/primary]',
                            subtitle='[warning]❏ uses/sets current problem | » supports --silent[/warning]',
                            subtitle_align='right',
                            title_align='left',
                            padding=(1, 2)))
    return ExitCodes.EXIT_OK

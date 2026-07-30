#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Built-in framework commands for shell v2: echo, clear, help.

`break` / `continue` / `exit` and `loop` are handled by the language itself
(lexer + interpreter), so they are not registered here.
"""
from __future__ import annotations

__all__ = []

import re
from typing import Iterable

from prompt_toolkit.completion import Completion
from rich.console import Group, RenderableType
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from solver.config import ExitCodes
from solver.shell.command import Command, Context, command
from solver.shell.docstring import help_model


# ------------------------------------------------------- echo ------------------------------------------------------- #
@command(requires='reader', name='echo', usage='\techo <text>')
def _echo(ctx: Context, *args: str) -> int:
    """Print the given text to the console, then succeed.

    Handy in command blocks to annotate progress or to surface a variable, since
    `{...}` references are substituted before the command runs — e.g.
    `echo solved {len(solved)} problems`.

    Args:
        ctx: [injected] The live shell context; the decorator supplies it.
        *args: The words to print. They are joined with single spaces and printed
            literally, with no rich markup interpretation.
    """
    ctx.console.print(' '.join(args), markup=False)
    return ExitCodes.EXIT_OK


# ------------------------------------------------------- clear ------------------------------------------------------ #
@command(requires='reader', name='clear', usage='\tclear', aliases=('cls',))
def _clear(ctx: Context, *_: str) -> int:
    """Clear the terminal screen and scrollback, then succeed.

    A convenience wrapper over the console's clear; equivalent to the shell `clear`. Takes
    no arguments — any given are ignored. Aliased as `cls`.

    Args:
        ctx: [injected] The live shell context; the decorator supplies it.
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


#: Inline code and **strong** spans in docstring prose — styled, not shown raw. Double
#: backticks come first: a docstring may still carry rST `` `` `` from before the sweep to
#: markdown, and matching the single-backtick form first would strand the outer pair.
_INLINE = re.compile(r'``([^`]+)``|`([^`]+)`|\*\*([^*]+)\*\*')

#: A line opening a bullet — `- item` / `* item`, never `**strong**`.
_BULLET = re.compile(r'[-•*]\s')


def _reflow(text: str) -> str:
    """Join a paragraph's hard-wrapped lines so the panel can rewrap to the terminal.

    A docstring is wrapped for the source file, not for whoever's terminal this is. Only
    plain prose is joined: every block reaching here has been dedented to the left margin,
    so a paragraph that is *still* indented is a literal block and keeps its line breaks,
    as does one opening a bullet.
    """
    out: list[str] = []
    for paragraph in re.split(r'\n\s*\n', text):
        lines = [line for line in paragraph.splitlines() if line.strip()]
        if not lines:
            continue
        flat = (all(line == line.lstrip() for line in lines)
                and not any(_BULLET.match(line) for line in lines))
        out.append(' '.join(lines) if flat else paragraph)
    return '\n\n'.join(out)


def _prose(text: str) -> Text:
    """Docstring text as styled `Text`, never as markup.

    Docstrings carry `[injected]`-style markers and bracketed prose that rich would read as
    style tags, so the text never reaches the markup parser. Inline code and **strong** spans
    are styled and their delimiters dropped, and rST's trailing `::` literal-block marker
    collapses to a plain colon.
    """
    text = _reflow(re.sub(r'::$', ':', text, flags=re.MULTILINE))
    out = Text()
    position = 0
    for span in _INLINE.finditer(text):
        out.append(text[position:span.start()])
        rst_code, code, strong = span.groups()
        inner = rst_code or code
        out.append(inner or strong, style='markdown.code' if inner else 'bold')
        position = span.end()
    out.append(text[position:])
    return out


def _heading(label: str) -> Text:
    """A section label inside the help panel — muted and lower-case, not a rule."""
    return Text(label.lower(), style='muted')


def _rows(rows: list[tuple[str, str]]) -> Table:
    """A two-column body table (name → prose), indented to the usage block's depth."""
    table = Table(show_header=False, box=None, padding=(0, 2), pad_edge=True)
    table.add_column(style='accent.dim', no_wrap=True)
    table.add_column(style='cmd.help', overflow='fold')
    for name, description in rows:
        table.add_row(name, _prose(description))
    return table


def _detail_panel(cmd: Command) -> Panel:
    """Full help for one command: summary, facts, prose, usage, arguments, free sections.

    Renders the shared :class:`~solver.shell.docstring.HelpModel`, which is the same model
    `update-docs` renders as markdown into `docs/commands-index.md` — so the published
    reference for a command *is* its `?` panel, not a second description of it.
    """
    model = help_model(cmd)
    blocks: list[RenderableType] = []

    head = Text(model.summary, style='accent.dim')
    for glyph, note in model.notes:
        head.append('\n')
        head.append(glyph, style='warning')
        head.append(f' {note}', style='accent.dim')
    blocks.append(head)

    if model.prose:
        blocks.extend((Text(), _prose(model.prose)))
    if model.usage:
        usage = Text('\n'.join(f'  {line}' for line in model.usage), style='accent.dim')
        blocks.extend((Text(), _heading('usage'), usage))
    if model.arguments:
        blocks.extend((Text(), _heading('arguments'), _rows(model.arguments)))
    for title, body in model.sections:
        # Indented to the depth of the usage block and the argument rows above it.
        blocks.extend((Text(), _heading(title), Padding(_prose(body), (0, 0, 0, 2))))

    aliases = f' [muted]·[/muted] [accent.dim]{", ".join(model.aliases)}[/accent.dim]' if model.aliases else ''
    return Panel(Group(*blocks),
                 border_style='panel.border',
                 title=f'[accent]▎[/accent] [cmd.name]{model.name}[/cmd.name]{aliases}',
                 title_align='left',
                 subtitle=f'[accent][[/accent][cmd.name]{model.fqn}[/cmd.name][accent]][/accent]',
                 subtitle_align='right',
                 padding=(1, 2))


@command(requires='reader', name='?',
         usage='\t? [command]',
         aliases=('help',),
         completer=_help_completer)
def _help(ctx: Context, *args: str) -> int:
    """List every command, or show detailed help for one command.

    With no argument, prints the catalogue: command, aliases, the profile it needs, and its
    description. Nothing there is abbreviated to a glyph — the facts one would stand for
    (the problem a command takes, the `--silent` it supports) are spelled out in words in
    the command's own panel, one `? <command>` away.

    With a command name or alias, prints that command's own panel — its description, the
    facts about it (the profile floor, and whether it takes a problem or supports
    `--silent`), the prose and free sections of its docstring, its usage, and a row per
    argument it accepts. It renders the same `HelpModel` that `update-docs` publishes as
    `docs/commands-index.md`, so the guide and the prompt cannot disagree;
    `docs/developer-guide.md` §3.8 is the docstring standard behind both. Returns non-zero
    if the named command is unknown.

    Aliased as `help`.

    Args:
        ctx: [injected] The live shell context; the decorator supplies it.
        *args: The command name or alias to describe. With none, lists every command.
    """
    reg = ctx.shell.registry
    if args:
        cmd: Command | None = reg.resolve(args[0])
        if cmd is None:
            ctx.console.print(f'[error]unknown command:[/error] {args[0]}')
            return ExitCodes.EXIT_NOTFOUND
        ctx.console.print(_detail_panel(cmd))
        return ExitCodes.EXIT_OK
    table = Table(show_header=True, header_style='muted', box=None, padding=(0, 2))
    table.add_column('command', style='accent.dim', no_wrap=True)
    table.add_column('aliases', style='accent.dim', no_wrap=True)
    table.add_column('requires', style='accent.dim', no_wrap=True)
    table.add_column('description', style='cmd.help')
    for cmd in reg.all():
        # Text(), not the bare string: a help line is prose we do not control, and rich
        # would read a bracketed span in one of them as a style tag.
        table.add_row(cmd.name, ' '.join(cmd.aliases), cmd.requires, Text(cmd.help))
    ctx.console.print(Panel(table,
                            border_style='panel.border',
                            title='[accent]▎[/accent] [primary]commands[/primary]',
                            title_align='left',
                            padding=(1, 2)))
    return ExitCodes.EXIT_OK

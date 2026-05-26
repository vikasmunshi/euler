#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Built-in framework commands for shell operations such as help, exit, clear, and
interaction with the system shell.

This module provides the foundational commands for the shell framework. It
includes commands to display help for shell commands, exit the shell, clear
the screen, run bash commands directly from the shell in the workspace, and
support for looping constructs like for-blocks.

"""
from __future__ import annotations

import ast
import os
import re
import shlex
import subprocess
from typing import Any, Iterable

from prompt_toolkit.completion import Completion
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from solver.core.problems import Problem, problems
from solver.shell.shell import Context, command


# ---------------------------------------------------------------------------
# Built-in framework commands (basics - help, clear screen, and exit)
# ---------------------------------------------------------------------------

@command(name='help',
         help='List commands or show help for a specific command.',
         usage='help [command]',
         aliases=('?',))
def _help(ctx: Context, *args: str) -> None:
    reg = ctx.shell.registry
    if args:
        cmd = reg.resolve(args[0])
        if cmd is None:
            ctx.console.print(f'[error]unknown command:[/error] {args[0]}')
            return
        body = Text()
        body.append(cmd.help or '(no description)', style='primary')
        if cmd.usage:
            body.append('\n\nusage: ', style='muted')
            body.append(cmd.usage, style='accent.dim')
        if cmd.aliases:
            body.append('\naliases: ', style='muted')
            body.append(', '.join(cmd.aliases), style='accent')
        ctx.console.print(Panel(body, border_style='panel.border',
                                title=f'[accent]▎[/accent] [cmd.name]{cmd.name}[/cmd.name]',
                                title_align='left', padding=(1, 2)))
        return
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style='cmd.name', no_wrap=True)
    table.add_column(style='cmd.help')
    for cmd in reg.all():
        table.add_row(cmd.name, cmd.help or '')
    ctx.console.print(Panel(table, border_style='panel.border',
                            title='[accent]▎[/accent] [primary]commands[/primary]',
                            title_align='left', padding=(1, 2)))


@command(name='exit',
         help='Exit the shell.',
         usage='exit',
         aliases=('quit', 'q'))
def _exit(ctx: Context, *_: str) -> bool:
    ctx.shell.stop()
    return True


@command(name='clear',
         help='Clear the screen.',
         usage='clear',
         aliases=('cls',))
def _clear(ctx: Context, *_: str) -> None:
    ctx.console.clear()


# ---------------------------------------------------------------------------
# Built-in framework commands (escape to shell in workspace)
# ---------------------------------------------------------------------------

def _bash_completer(ctx: Context, incomplete: str) -> Iterable[str | Completion]:
    """Completer for the `!` / `bash` / `sh` shell-passthrough command.

    * First positional token (the shell command itself): list executable
      files found in `/bin`, `/usr/bin`, `/usr/local/bin`, `~/local/bin`,
      and `~/.local/bin` (deduplicated, first occurrence wins).
    * Subsequent tokens: try the command's own completions via
      `bash -c "compgen ..."`; merge with workspace files.
    """
    # Count completed positional tokens already on the line.
    # When *incomplete* is non-empty it is the last entry of `ctx.argv`,
    # which we don't want to count as "already supplied".
    pos_count = len(ctx.argv) - (1 if incomplete else 0)
    if pos_count <= 0:
        # Complete a shell command name from well-known bin dirs.
        seen: set[str] = set()
        results: list[str] = []
        bin_dirs = (
            '/bin',
            '/usr/bin',
            '/usr/local/bin',
            os.path.expanduser('~/local/bin'),
            os.path.expanduser('~/.local/bin'),
        )
        for d in bin_dirs:
            try:
                entries = os.listdir(d)
            except OSError:
                continue
            for entry in entries:
                if entry in seen or not entry.startswith(incomplete):
                    continue
                full = os.path.join(d, entry)
                if os.access(full, os.X_OK) and os.path.isfile(full):
                    seen.add(entry)
                    results.append(entry)
        results.sort()
        return results
    # Subsequent tokens: command-specific completions + workspace files.
    results = []
    seen = set()
    # Ask bash for command-specific completions via compgen.
    cmd_name = ctx.argv[0]
    try:
        q_cmd = shlex.quote(cmd_name)
        q_inc = shlex.quote(incomplete)
        script = (
            '{ '
            'source /etc/bash_completion; '
            'source ~/.bash_completion; '
            f'declare -F _completion_loader >/dev/null && _completion_loader {q_cmd}; '
            '} >/dev/null 2>&1; '
            # Extract the real completion function registered for the command.
            f'_fn=$(complete -p {q_cmd} 2>/dev/null | sed -n "s/.*-F \\([^ ]*\\).*/\\1/p"); '
            f'if [ -n "$_fn" ]; then COMP_WORDS=({q_cmd} {q_inc}); COMP_CWORD=1; '
            f'COMP_LINE={shlex.quote(cmd_name + " " + incomplete)}; '
            f'COMP_POINT=${{#COMP_LINE}}; "$_fn" {q_cmd} {q_inc} {q_cmd} 2>/dev/null; '
            f'printf "%s\\n" "${{COMPREPLY[@]}}"; fi; '
            f'compgen -o default -- {q_inc} 2>/dev/null'
        )
        proc = subprocess.run(
            ['bash', '-c', script],
            capture_output=True, text=True, timeout=2, cwd=ctx.shell.workspace, check=False,
        )
        for line in proc.stdout.splitlines():
            line = line.strip()
            if line and line not in seen:
                seen.add(line)
                results.append(line)
    except (OSError, subprocess.TimeoutExpired):
        pass
    # Workspace files as a fallback / supplement.
    try:
        for f in sorted(ctx.shell.workspace.iterdir()):
            if f.name.startswith(incomplete) and f.name not in seen:
                seen.add(f.name)
                results.append(f.name)
    except OSError:
        pass
    return results


@command(name='!',
         help='Run a bash command in the workspace.',
         usage='! <command ...>',
         aliases=('sh', 'bash',),
         completer=_bash_completer)
def _bash(ctx: Context, *args: str) -> None:
    cmdline = ctx.raw_line.lstrip()
    # Strip the invoking token so the rest is forwarded verbatim to the shell,
    # preserving quoting and operators.
    # '!' has no space after it (e.g. '!ls'); named aliases (sh/bash) are
    # separated by whitespace.
    if cmdline.startswith('!'):
        cmdline = cmdline[1:].lstrip()
    else:
        first_space = cmdline.find(' ')
        cmdline = cmdline[first_space:].lstrip() if first_space != -1 else ''
    if not cmdline:
        ctx.console.print('[muted]usage:[/muted] [accent]! <command ...>[/accent]')
        return
    try:
        proc = subprocess.run(cmdline, shell=True, cwd=ctx.shell.workspace, check=False)
    except OSError as exc:
        ctx.console.print(f'[error]exec error:[/error] {exc}')
        return
    if proc.returncode != 0:
        ctx.console.print(f'[muted]exit[/muted] [warning]{proc.returncode}[/warning]')


# ---------------------------------------------------------------------------
# Built-in framework commands (looping with for-blocks)
# ---------------------------------------------------------------------------

def _parse_for_block(raw: str) -> tuple[str, str, list[str]]:
    """Parse a brace-delimited for-block from *raw* (multi-line string).

    Expected format::

        for <var> in <iterable> {
          cmd1 ...
          cmd2 ...
        }

    Returns '(var, iterable_expr, body_lines)'.  Raises 'ValueError' on
    malformed input.
    """
    lines = raw.strip().splitlines()
    if not lines:
        raise ValueError('empty block')
    header = lines[0].strip()
    m = re.match(r'^for\s+(\w+)\s+in\s+(.+?)\s*\{\s*$', header)
    if not m:
        raise ValueError(f'invalid for header {header!r}\n' 'expected:  for <var> in <iterable> {')
    var = m.group(1)
    iterable_expr = m.group(2).strip()
    body_lines: list[str] = []
    for line in lines[1:]:
        if line.strip() == '}':
            break
        body_lines.append(line.strip())
    return var, iterable_expr, body_lines


def _expand_iterable(expr: str) -> list[Any]:
    """Expand an iterable expression string to a concrete list.

    Supported forms:

    * '1..10'        — inclusive integer range (step +1 or −1 as needed)
    * 'range(...)'   — Python :func:`range` call; evaluated safely
    * '[1, 'a', ...]'— Python list literal via :func:`ast.literal_eval`
    * '1,5,10'       — comma-separated values; each coerced to int/float/str
    """
    expr = expr.strip()
    # Integer range: 1..10 (inclusive on both ends)
    m = re.match(r'^(-?\d+)\.\.(-?\d+)$', expr)
    if m:
        start, end = int(m.group(1)), int(m.group(2))
        step = 1 if end >= start else -1
        return list(range(start, end + step, step))
    # Python range(): range(10) / range(1,11) / range(1,11,2)
    m = re.match(r'^range\((.+)\)$', expr)
    if m:
        args = ast.literal_eval(f'({m.group(1)},)')
        return list(range(*args))
    # Python list literal: [1, 2, 3] / ['a', 'b']
    if expr.startswith('['):
        return list(ast.literal_eval(expr))
    # Comma-separated bare values: 1,5,10 / a,b,c
    if ',' in expr:
        result: list[Any] = []
        for part in expr.split(','):
            part = part.strip()
            try:
                result.append(int(part))
            except ValueError:
                try:
                    result.append(float(part))
                except ValueError:
                    result.append(part)
        return result
    raise ValueError(f'cannot expand iterable: {expr!r}')


def _substitute(line: str, var: str, val: Any) -> str:
    """Replace every token in *line* that is exactly *var* with *val*."""
    try:
        tokens = shlex.split(line, posix=True)
    except ValueError:
        tokens = line.split()
    replaced = [str(val) if tok == var else tok for tok in tokens]
    if not replaced:
        return ''
    # Do not quote the first token: it may be a dispatch sigil ('!cmd', '?cmd')
    # and shlex.quote would hide the leading '!'/'?' from dispatch's rewrite logic.
    tail = [shlex.quote(tok) for tok in replaced[1:]]
    return ' '.join([replaced[0]] + tail)


@command(name='for',
         help='Loop over values, executing a block of commands.',
         usage=(
                 'for <var> in <iterable> {\n  cmd-block\n}\n\n'
                 'iterables:\n'
                 '  1..10          inclusive integer range\n'
                 '  range(1, 11)   Python range()\n'
                 '  [1, 5, 10]     list literal\n'
                 '  1,5,10         comma-separated values\n'
                 '  problems       list of problem numbers\n'
                 '  solved         list of solved problem numbers\n\n'
                 'examples:\n\n'
                 'for i in 1..10 {\n  ! echo i\n}\n\n'
                 'for num in problems {\n  init num\n  reinit\n  stack\n  reset\n}\n'
                 'for num in solved {\n  init num\n  benchmark all\n  stack\n  reset\n}\n'
                 'for num in solved {\n  init num\n  eval show=true\n  reset\n}\n'
         ))
def _for(ctx: Context, *_args: str) -> None:
    try:
        var, iterable_expr, body_lines = _parse_for_block(ctx.raw_line)
        iterable_expr = iterable_expr.strip()
        if iterable_expr == 'problems':
            values = [problem.number for problem in problems.problems_list]
        elif iterable_expr == 'solved':
            values = [problem.number for problem in problems.solved_problems]
        else:
            values = _expand_iterable(iterable_expr)
    except ValueError as exc:
        ctx.console.print(f'[error]for error:[/error] {exc}')
        return
    body_lines = [ln for ln in body_lines if ln]
    if not body_lines:
        ctx.console.print('[muted]empty body — nothing to do[/muted]')
        return
    for val in values:
        for body_line in body_lines:
            substituted = _substitute(body_line, var, val)
            try:
                if ctx.shell.dispatch(substituted):
                    return  # exit was requested from inside the loop
            except KeyboardInterrupt:
                ctx.console.print('[muted]^C — loop interrupted[/muted]')
                return


# ---------------------------------------------------------------------------
# Built-in framework commands (progress tracker)
# ---------------------------------------------------------------------------

@command(name='progress',
         help='Print progress statistics about Euler problems.',
         usage='progress', )
def _progress(ctx: Context) -> None:
    """Print statistics about the Euler problems."""
    total: int = len(problems.problems_list)
    solved: int = len(problems.solved_problems)
    next_to_solve: Problem = next((problem for problem in problems.problems_list
                                   if problem not in problems.solved_problems), problems.problems_list[-1])
    # Calculate bar widths (max 50 characters total)
    bar_width: int = 50
    solved_width: int = int((solved / total) * bar_width)
    unsolved_width: int = bar_width - solved_width
    # Create the bar
    solved_bar = '█' * solved_width
    unsolved_bar = '░' * unsolved_width
    ctx.console.print(
        f'\n[green]{solved_bar}[/green][dim]{unsolved_bar}[/dim]\n'
        f'[muted]{"Progress:":>18} {solved}/{total} ({(solved / total * 100) if total > 0 else 0:.1f}%)[/muted]'
        f'\n[muted]{"Next to solve:":>18} {next_to_solve}[/muted]\n'
    )

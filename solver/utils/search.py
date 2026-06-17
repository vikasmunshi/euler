#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""'find' command: grep the solution stack for a regular expression.

Unlike a plain filesystem grep, this walks the *logical* stack — iterating over
problems (all, or only solved) and reading each file through
:func:`read_stack_file`, which transparently decrypts the encrypted files of
problems above 100.  Matches are printed as '<dir>/<file>:<line> <text>' with
the matched substring highlighted.
"""
from __future__ import annotations

__all__ = ['search']

import re
from pathlib import Path
from typing import Literal

from rich.markup import escape

from solver.config import ExitCodes, config
from solver.core.problems import Problem, problems
from solver.core.stack import read_stack_file, stack_base_dir
from solver.shell import console, register
from solver.utils.path_utils import iterdir_recursive


def _highlight(re_query: re.Pattern[str], text: str) -> str:
    """Return *text* as rich markup with every match of *re_query* emphasised.

    Both the matched substrings and the surrounding text are escaped with
    :func:`rich.markup.escape`, so characters that resemble markup (e.g. the
    '[int]' in a type hint, or a stray '[/]') render literally instead of
    being swallowed as tags or raising a 'MarkupError'.
    """
    parts: list[str] = []
    pos: int = 0
    for match in re_query.finditer(text):
        parts.append(escape(text[pos:match.start()]))
        parts.append(f'[bold red]{escape(match.group())}[/bold red]')
        pos = match.end()
    parts.append(escape(text[pos:]))
    return ''.join(parts)


@register(
    help_text='Find content in the stack.',
    aliases=('find',),
)
def search(query: str,
           *files: Literal['*', 'py', 'c', 'html', 'json'],
           scope: Literal['problems', 'solved'] = 'solved') -> int:
    """Search the solution stack for a case-insensitive regular expression.

    For every problem in scope, each matching stack file is read (decrypted as
    needed) and scanned line by line; every matching line is printed as
    '<stack-dir>/<file>:<line> <text>' with the matched substring highlighted.
    A blank line separates the matches of one problem from the next.

    Args:
        query:  Regular expression to search for, matched case-insensitively
                against each line ('re.search', so it need not match the whole
                line).
        *files: File extensions to include, given without the leading dot.
                Defaults to 'py html' when omitted; '*' expands to the full
                set 'py c html json'.
        scope:  Which problems to search: 'solved' (default) restricts to
                solved problems; 'problems' covers every known problem.
    """
    # Resolve the extension filter, then prefix each with '.' for endswith().
    extensions: tuple[str, ...] = files or ('py', 'html')
    if '*' in extensions:
        extensions = ('py', 'c', 'html', 'json')
    suffixes: tuple[str, ...] = tuple(f'.{ext}' for ext in extensions)
    try:
        re_query = re.compile(query, re.IGNORECASE)
    except re.error as exc:
        console.print(f'[error]invalid regex:[/error] {exc}')
        return ExitCodes.EXIT_ERROR
    problems_in_scope: list[Problem] = problems.problems_list if scope == 'problems' else problems.solved_problems
    for problem in problems_in_scope:
        found: bool = False
        stack_dir: Path = stack_base_dir(problem.number)
        for filename in iterdir_recursive(stack_dir, rt='str'):
            # Stored encrypted files carry a '.enc' suffix on disk, but read_stack_file
            # expects the logical name; strip it before filtering and reading.
            filename = filename.removesuffix('.enc')
            if not any(filename.endswith(suffix) for suffix in suffixes):
                continue
            content: bytes = read_stack_file(problem.number, filename)[0]
            for line_num, line in enumerate(content.decode('utf-8').splitlines(), start=1):
                if re_query.search(line):
                    found = True
                    console.print(f'[dim]{stack_dir.relative_to(config.root_dir).as_posix()}/[/dim]'
                                  f'[accent.dim]{filename}[/accent.dim][dim]:{line_num}[/dim] '
                                  f'{_highlight(re_query, line.strip())}')
        if found:
            console.print()
    return ExitCodes.EXIT_OK

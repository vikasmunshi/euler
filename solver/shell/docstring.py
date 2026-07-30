#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Reading a command's docstring: the shape both `?` and `check-commands` rely on.

A command docstring is part of the command contract, not an internal note — it is what
`? <command>` renders and what `update-docs` embeds in `docs/commands-index.md`. The
standard it follows is `docs/developer-guide.md` §3.8; this module is the one parser for
it, so the renderer (`solver/shell/builtins.py`) and the checker
(`solver/utils/doclint.py`) can never disagree about what a docstring says.

The grammar, such as it is::

    <summary line>          the first line

    <prose paragraphs>      everything up to the first heading

    Args:                   a heading: `Capitalised:` alone on a line
        name: description   an entry at the section's own indent
            continued       anything indented further continues the entry above

    Notes:                  any other heading is free text, rendered verbatim

An entry's description may open with a `[marker]` naming where the value comes from —
`[injected]` for the `Context` the decorator supplies, `[problem]` for the problem
special. :func:`split_marker` separates it from the prose.
"""
from __future__ import annotations

__all__ = ['CONTINUATION_INDENT', 'ENTRY_RE', 'GLYPH_ASKS', 'GLYPH_PROBLEM', 'GLYPH_REQUIRES',
           'GLYPH_SILENT', 'HelpModel', 'MARKER_ASKED', 'MARKER_INJECTED', 'MARKER_PROBLEM',
           'NOTE_ASKS', 'NOTE_PROBLEM', 'NOTE_SILENT', 'SILENT_HELP', 'command_doc', 'entries',
           'help_model', 'requires_note', 'sections', 'split_marker']

import inspect
import re
from dataclasses import dataclass
from typing import Any

from solver.auth import LADDER

#: The `Context` the adapter injects: never typed at the prompt, never in usage.
MARKER_INJECTED: str = 'injected'
#: The problem special: a bare number or `problem=N`, or omitted to inherit the current one.
MARKER_PROBLEM: str = 'problem'
#: A parameter the adapter offers to fill in when it is left out (developer-guide §3.11).
MARKER_ASKED: str = 'asked'

#: A section heading: `Args:` / `Repeats:` alone on a line, at the docstring's left margin.
_SECTION = re.compile(r'^([A-Z][\w /-]*):\s*$')
#: One `Args:` entry: `name: description`, the name optionally starred for a variadic.
#: Public because the checker validates entry *placement* with the same pattern the
#: parser reads entries with — two spellings of "what is an entry" would drift.
ENTRY_RE = re.compile(r'^(\*{0,2}[A-Za-z_]\w*)\s*:\s*(.*)$')

#: How far a wrapped description indents past its entry: four columns, never aligned into
#: a description column (developer-guide §3.8 rule 3).
CONTINUATION_INDENT: int = 4
#: A leading `[marker]` on an entry's description.
_MARKER = re.compile(r'^\[(\w+)]\s*')


def command_doc(cmd: Any) -> str:
    """The command function's cleaned docstring (decorators unwrapped), or ''.

    `@register` registers an adapter that `functools.wraps` the real function, so what
    comes back is the docstring as written in the source — the same text `update-docs`
    embeds. *cmd* is a `Command`, typed loosely to keep this module free of the registry.
    """
    func = cmd.func
    while hasattr(func, '__wrapped__'):
        func = func.__wrapped__
    return inspect.getdoc(func) or ''


def sections(doc: str) -> tuple[list[str], dict[str, list[str]]]:
    """Split *doc* into the lines before the first heading and its titled sections.

    Sections come back as a `lower-cased title → body lines` mapping, in the order they
    appear (a repeated title keeps the last body — the standard forbids repeats anyway).
    """
    lead: list[str] = []
    found: dict[str, list[str]] = {}
    body: list[str] | None = None
    for line in doc.splitlines():
        heading = _SECTION.match(line)
        if heading:
            body = []
            found[heading.group(1).lower()] = body
            continue
        (lead if body is None else body).append(line)
    return lead, found


def entries(body: list[str]) -> list[tuple[str, str]]:
    """Parse an `Args:` body into `(name, description)` pairs.

    An entry starts at the section's own indent; anything indented further continues the
    entry above it, so a description may wrap freely and may contain colons.
    """
    base: int | None = None
    out: list[tuple[str, str]] = []
    for line in body:
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        if base is None:
            base = indent
        match = ENTRY_RE.match(line.strip()) if indent <= base else None
        if match:
            out.append((match.group(1), match.group(2).strip()))
        elif out:
            out[-1] = (out[-1][0], f'{out[-1][1]} {line.strip()}'.strip())
    return out


def split_marker(description: str) -> tuple[str, str]:
    """Split an entry's description into its leading `[marker]` and the prose after it.

    Returns `('', description)` when there is no marker — the ordinary case, an argument
    the user types.
    """
    match = _MARKER.match(description)
    if match is None:
        return '', description.strip()
    return match.group(1), description[match.end():].strip()


# ── the help model: one description of a command, rendered two ways ─────────────────────

#: The legend glyphs. Each marks a *fact about the command* that its signature cannot show,
#: and each is shown by every view of the command — `?`'s catalogue and panel, and the
#: generated tables and index — so they are defined once, here, beside the notes they head.
GLYPH_REQUIRES: str = '⚑'
GLYPH_PROBLEM: str = '❏'
GLYPH_SILENT: str = '»'
GLYPH_ASKS: str = '✎'

#: The two fixed notes. The third (`GLYPH_REQUIRES`) is per-command: see `requires_note`.
NOTE_PROBLEM: str = 'uses/sets current problem.'
NOTE_SILENT: str = 'supports --silent to suppress output.'
NOTE_ASKS: str = 'asks for anything you leave out.'

#: The description of the synthetic `--silent` flag — identical on every quietable command,
#: which is exactly why no docstring carries it (developer-guide §3.8).
SILENT_HELP: str = "Suppress this command's output; errors and the result line still show."


def requires_note(requires: str) -> str:
    """The floor as a sentence: "needs contributor or above.", or "needs admin." at the top.

    The ladder is inclusive upward — a floor admits every rung above it — so naming only the
    floor would understate who may run the command. The top rung has nothing above it, and
    "or above" there would be a lie.
    """
    if not requires:
        return ''
    if LADDER and requires == LADDER[-1]:
        return f'needs {requires}.'
    return f'needs {requires} or above.'


@dataclass(frozen=True)
class HelpModel:
    """Everything `?` shows about one command, medium-independent.

    Built once by :func:`help_model` and rendered twice: as a rich panel by
    `solver/shell/builtins.py`, and as markdown by `update-docs` for
    `docs/commands-index.md`. Two renderers over one model is what makes the published
    reference *be* the help rather than resemble it — the alternative, each view reading the
    docstring its own way, is how they drifted apart before.
    """
    name: str
    aliases: tuple[str, ...]
    fqn: str
    summary: str
    #: `(glyph, sentence)` facts about the command, in reading order.
    notes: list[tuple[str, str]]
    prose: str
    usage: list[str]
    #: `(name, description)` for each argument the user can type — the injected `Context` is
    #: dropped (it cannot be typed) and the synthetic `silent` flag is appended.
    arguments: list[tuple[str, str]]
    #: `(title, body)` for each free section, `Args:` excluded.
    sections: list[tuple[str, str]]


def dedent(lines: list[str]) -> list[str]:
    """Strip the common leading indent from a block, keeping relative indents."""
    pad = min((len(line) - len(line.lstrip()) for line in lines if line.strip()), default=0)
    return [line[pad:] if line.strip() else '' for line in lines]


def help_model(cmd: Any) -> HelpModel:
    """Read *cmd*'s docstring and registration into the one model both renderers use.

    *cmd* is a `Command`, typed loosely to keep this module free of the registry.
    """
    lead, found = sections(command_doc(cmd))
    notes: list[tuple[str, str]] = []
    if note := requires_note(cmd.requires):
        notes.append((GLYPH_REQUIRES, note))
    if cmd.uses_problem:
        notes.append((GLYPH_PROBLEM, NOTE_PROBLEM))
    if cmd.asks:
        notes.append((GLYPH_ASKS, NOTE_ASKS))
    if cmd.quietable:
        notes.append((GLYPH_SILENT, NOTE_SILENT))
    arguments = [(name, rest) for name, description in entries(found.get('args', []))
                 for marker, rest in [split_marker(description)]
                 if marker != MARKER_INJECTED]
    if cmd.quietable:
        arguments.append(('silent', SILENT_HELP))
    free = [(title, '\n'.join(dedent(body)).strip('\n'))
            for title, body in found.items() if title != 'args']
    return HelpModel(
        name=cmd.name,
        aliases=tuple(cmd.aliases),
        fqn=f'{cmd.func.__module__}.{cmd.func.__name__}',
        summary=cmd.help or '(no description)',
        notes=notes,
        prose='\n'.join(dedent(lead[1:])).strip('\n'),
        usage=[line.replace('\t', '').rstrip() for line in cmd.usage.splitlines() if line.strip()],
        arguments=arguments,
        sections=[(title, body) for title, body in free if body.strip()],
    )

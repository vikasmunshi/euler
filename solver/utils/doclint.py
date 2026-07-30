#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The `check-commands` command: hold every command docstring to the documented standard.

A command's docstring is user-facing twice over — the panel `? <command>` prints and the
per-command reference `update-docs` writes into `docs/commands-index.md` — so its shape is
part of the command contract, not a matter of taste. The standard lives in
`docs/developer-guide.md` §3.8; this module is its enforcement, reporting each breach as a
`command | rule | detail` row.

What it checks, one rule per name reported:

* `missing-docstring` / `summary`  — a docstring exists, opening with a single-line
  summary that ends in a period and is followed by a blank line.
* `banned-section`                 — no `Returns:` / `Raises:` (boilerplate: the exit code
  is always an `int` and the adapter catches everything), and parameter sections spelled
  `Args:` rather than `Arguments:` / `Parameters:`.
* `args-section`                   — an `Args:` section exists exactly when the function
  takes parameters.
* `undocumented` / `unknown-arg` / `arg-order` / `empty-description` — the documented
  names are the signature's names, in the signature's order, each with prose.
* `indent`                         — entries sit at the section's indent and wrapped
  descriptions four columns past it, rather than aligned into a description column.
* `marker`                         — a parameter whose value does not simply come from the
  command line carries the marker saying where it *does* come from: `[injected]` for the
  injected `Context`, `[problem]` for the problem special, `[asked]` for one the adapter
  offers to fill in. Ordinary arguments carry none of them.
* `summary-length` / `line-length` — the summary fits a catalogue cell (80 columns) and
  every rendered line (post-`inspect.getdoc`) fits the panel and the fenced doc block (100).
* `rst-literal`                    — inline code is written with single backticks, the one
  spelling that renders in all three places a docstring is read.
"""
from __future__ import annotations

__all__ = ['check_commands', 'findings']

import inspect
import re
from dataclasses import dataclass

from rich.table import Table
from rich.text import Text

from solver.config import ExitCodes
from solver.shell import console, register
from solver.shell.command import Command, Context, registry
# The docstring grammar is read in one place (`solver/shell/docstring.py`) so the checker
# and the `?` renderer can never disagree about what a docstring says; likewise
# `_is_problem_annotation` is the adapter's own answer to what makes a parameter the
# problem special, imported rather than re-implemented so the rule cannot drift from it.
from solver.shell.dialogue import Ask
from solver.shell.docstring import (CONTINUATION_INDENT, ENTRY_RE, MARKER_ASKED, MARKER_INJECTED,
                                    MARKER_PROBLEM, command_doc, entries, sections, split_marker)
from solver.shell.register import _is_problem_annotation

#: Section titles that must never appear, mapped to the reason they are refused.
BANNED_SECTIONS: dict[str, str] = {
    'returns': 'every command returns an `int` exit code; say so in prose only when it is non-obvious',
    'yields': 'a command is not a generator',
    'raises': 'the adapter catches everything a command raises',
    'arguments': 'spell the parameter section `Args:`',
    'parameters': 'spell the parameter section `Args:`',
}

#: Width a rendered docstring line must stay under: it is shown inside a panel and inside a
#: fenced block in `docs/commands-index.md`, neither of which can scroll sideways.
MAX_WIDTH: int = 100

#: Width the summary line must stay under. It is the command's *only* description — the
#: catalogue cell `?` prints and the generated tables publish — so it has a tighter budget
#: than the prose below it.
MAX_SUMMARY: int = 80

#: rST inline literals. The docstrings are markdown-flavoured: single backticks, so that one
#: spelling renders everywhere it is read (panel, guide, index).
_RST_LITERAL = re.compile(r'``[^`\n]+``')


@dataclass(frozen=True)
class Finding:
    """One breach of the docstring standard, as reported to the operator."""
    command: str
    rule: str
    detail: str


def parameters(cmd: Command) -> list[inspect.Parameter]:
    """The command function's parameters, with pure throwaways (`_`, `*_`) dropped.

    Annotations are evaluated (`eval_str=True`) so the marker rules can recognise the
    injected `Context` and the problem special by type rather than by name.
    """
    func = cmd.func
    while hasattr(func, '__wrapped__'):
        func = func.__wrapped__
    try:
        params = list(inspect.signature(func, eval_str=True).parameters.values())
    except (TypeError, ValueError, NameError):
        return []
    return [p for p in params if p.name.strip('_')]


def _stars(param: inspect.Parameter) -> str:
    """The stars an entry's name must carry: `*` for `*args`, `**` for `**kwargs`, else ''."""
    if param.kind is inspect.Parameter.VAR_POSITIONAL:
        return '*'
    if param.kind is inspect.Parameter.VAR_KEYWORD:
        return '**'
    return ''


def expected_marker(param: inspect.Parameter) -> str:
    """The marker *param* must carry, or '' for an ordinary argument the user types.

    `asked` for a parameter carrying an `Ask` (the adapter offers to fill it in), `injected`
    for the `Context` the decorator supplies, `problem` for the problem special.
    """
    metadata = getattr(param.annotation, '__metadata__', ())
    if any(isinstance(item, Ask) for item in metadata):
        return MARKER_ASKED
    annotation = param.annotation.__origin__ if metadata else param.annotation
    if annotation is Context:
        return MARKER_INJECTED
    if param.name == 'problem' and _is_problem_annotation(annotation):
        return MARKER_PROBLEM
    return ''


def indent_findings(body: list[str]) -> list[str]:
    """Report every `Args:` line that sits at neither the entry indent nor the continuation one.

    The standard wraps a description four columns past its entry name rather than aligning
    descriptions into a column, so that renaming a parameter never reflows its neighbours.
    """
    base: int | None = None
    out: list[str] = []
    for line in body:
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        if base is None:
            base = indent
        if indent == base and ENTRY_RE.match(line.strip()):
            continue
        if indent == base + CONTINUATION_INDENT:
            continue
        out.append(f'`{line.strip()[:40]}…` is indented {indent}; an entry indents {base} '
                   f'and a wrapped description {base + CONTINUATION_INDENT}')
    return out


def check(cmd: Command) -> list[Finding]:
    """Every way *cmd*'s docstring departs from the standard, in reading order."""
    out: list[Finding] = []

    def report(rule: str, detail: str) -> None:
        out.append(Finding(cmd.name, rule, detail))

    doc = command_doc(cmd)
    if not doc.strip():
        report('missing-docstring', 'the command has no docstring')
        return out
    lines = doc.splitlines()
    summary = lines[0].strip()
    if not summary.endswith('.'):
        report('summary', f'the summary line must end with a period: {summary!r}')
    if len(lines) > 1 and lines[1].strip():
        report('summary', 'the summary must be one line, followed by a blank line')
    if len(summary) > MAX_SUMMARY:
        report('summary-length', f'the summary is {len(summary)} columns (max {MAX_SUMMARY}); '
                                 'it has to fit the catalogue table')
    for literal in _RST_LITERAL.findall(doc):
        report('rst-literal', f'{literal} — write inline code with single backticks')
    for number, line in enumerate(lines, start=1):
        if len(line) > MAX_WIDTH:
            report('line-length', f'line {number} is {len(line)} columns (max {MAX_WIDTH})')

    lead, found = sections(doc)
    for title, reason in BANNED_SECTIONS.items():
        if title in found:
            report('banned-section', f'`{title.capitalize()}:` — {reason}')

    params = parameters(cmd)
    documented = entries(found.get('args', []))
    if params and 'args' not in found:
        missing = ', '.join(p.name for p in params)
        report('args-section', f'no `Args:` section, but the command takes: {missing}')
        return out
    if not params and 'args' in found:
        report('args-section', 'an `Args:` section, but the command takes no parameters')

    for detail in indent_findings(found.get('args', [])):
        report('indent', detail)

    names = [p.name for p in params]
    by_name = {p.name: p for p in params}
    given = [name.lstrip('*') for name, _ in documented]
    for name in names:
        if name not in given:
            report('undocumented', f'`{name}` is not described')
    for name in given:
        if name not in names:
            report('unknown-arg', f'`{name}` is described but is not a parameter')
    shared = [name for name in given if name in names]
    if shared != [name for name in names if name in given]:
        report('arg-order', f'described in the order {", ".join(given)}; '
                            f'the signature says {", ".join(names)}')

    for raw, description in documented:
        name = raw.lstrip('*')
        param = by_name.get(name)
        if param is None:
            continue
        if raw != f'{_stars(param)}{name}':
            report('arg-name', f'`{raw}` should be written `{_stars(param)}{name}`')
        marker, rest = split_marker(description)
        wanted = expected_marker(param)
        if not rest:
            report('empty-description', f'`{name}` is listed with no description')
        if wanted and marker != wanted:
            report('marker', f'`{name}` must be described as `[{wanted}] …`')
        if not wanted and marker:
            report('marker', f'`{name}` is an ordinary argument and takes no `[{marker}]` marker')

    return out


def findings(name: str = '') -> list[Finding]:
    """Check the whole registry, or the single command *name* resolves to."""
    if name:
        cmd = registry.resolve(name)
        return check(cmd) if cmd else [Finding(name, 'unknown-command', 'no such command')]
    return [f for cmd in registry.all() for f in check(cmd)]


def _name_completer(_: Context, incomplete: str) -> list[str]:
    """Suggest registered command names (aliases included) for the `name` filter."""
    return [name for name in registry.names() if name.startswith(incomplete)]


@register(requires='admin', quietable=True, completers={'name': _name_completer})
def check_commands(name: str = '') -> int:
    """Report every command docstring that breaks the documented standard.

    The standard is `docs/developer-guide.md` §3.8; the rules are listed in this module's
    docstring. Findings print as `command | rule | detail` rows, and the exit code is
    non-zero when there is at least one — so the command gates a chain and serves as the
    docstring lane of `scripts/linters/check.sh solver`.

    **Admin-floored on purpose, not out of caution.** Registration is itself
    profile-filtered (`solver/shell/command.py`): a command above your floor is never
    registered, so `registry.all()` returns only what *you* may run. Checking from a lesser
    profile would pass by never looking at the commands it cannot see — the same reasoning
    that floors `update-docs`.

    Args:
        name: Check only the command (or alias) named, instead of the whole registry.
            Defaults to '', which checks every registered command.
    """
    found = findings(name)
    checked = 1 if name else len(registry.all())
    if not found:
        console.print(f'[success]docstrings conform[/success] [muted]({checked} command(s) checked)[/muted]')
        return ExitCodes.EXIT_OK
    table = Table(show_header=True, header_style='muted', box=None, padding=(0, 2))
    table.add_column('command', style='cmd.name', no_wrap=True)
    table.add_column('rule', style='warning', no_wrap=True)
    table.add_column('detail', style='cmd.help', overflow='fold')
    for finding in found:
        # The detail quotes docstring text — `[injected]` and friends are markup to rich,
        # so hand it a `Text` and let the column's style do the colouring.
        table.add_row(finding.command, finding.rule, Text(finding.detail))
    console.print(table)
    offenders = len({f.command for f in found})
    console.print(f'[error]{len(found)} finding(s)[/error] [muted]in {offenders} of {checked} command(s)[/muted]')
    return ExitCodes.EXIT_ERROR

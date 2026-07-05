#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Regenerate the machine-maintained sections of the guides under `docs/`.

Some parts of the documentation mirror the live command registry (the command
table in the user guide, the per-command reference in `commands-index.md`), and
the authorization policy `solver/commands.csv` is likewise reconciled with the
registry (see :func:`_sync_commands`). Rather than hand-edit them whenever a
command's name, alias, help text, or usage changes, those sections are delimited
with HTML marker comments and rebuilt from the registry::

    <!-- GEN:command-table -->
    ...generated content (do not edit by hand)...
    <!-- /GEN:command-table -->

Each `GEN:<name>` block is filled by the generator registered under `<name>`
in :data:`GENERATORS`. Everything outside the markers is left untouched, so prose
and generated reference live in the same file without fighting each other.

The work is exposed as the `update-docs` shell command (`update_docs`): run it
from within the solver shell, or non-interactively for a pre-commit / CI lane —
`solver "update-docs"` to rewrite, `solver "update-docs --check"` to verify
(exit 1 if any doc is out of date, writing nothing).
"""
from __future__ import annotations

import ast
import csv
import inspect
import io
import re
from pathlib import Path
from typing import Callable

from solver.config import ExitCodes, config
from solver.shell import console, register
from solver.shell.command import Command, Context, registry
from solver.utils.loader import load_commands, update_modules

#: Cells read as "granted"/"on" in the modules.csv / commands.csv policy files.
_TRUTHY: frozenset[str] = frozenset({'true', '1', 'yes'})
#: Authorization profiles, in descending order of privilege.
_PROFILES: tuple[str, ...] = ('admin', 'user', 'guest')

#: The docs directory whose marked blocks we maintain.
ROOT: Path = config.root_dir
DOCS_DIR: Path = config.docs_dir

#: Strips rich console markup (`[accent]`, `[/warning]`, …) from help strings.
_MARKUP = re.compile(r'\[/?[\w.]+\]')

#: Trailing legend glyphs the registry appends to a command's help text.
#:   ❏ takes an optional problem number (default current) · » supports --silent
_LEGEND: dict[str, str] = {
    '❏': 'takes an optional problem number (defaults to the current problem)',
    '»': 'supports `--silent`',
}


def _clean_help(help_text: str) -> tuple[str, list[str]]:
    """Return *(description, glyphs)* — markup-stripped help and its legend glyphs."""
    text = _MARKUP.sub('', help_text).strip()
    glyphs = [g for g in _LEGEND if g in text]
    for g in _LEGEND:
        text = text.replace(g, '')
    return ' '.join(text.split()), glyphs


def _aliases(cmd: Command) -> str:
    """Render a command's aliases as inline code, or an em dash when it has none."""
    return ', '.join(f'`{a}`' for a in cmd.aliases) if cmd.aliases else '—'


def _heading_text(cmd: Command) -> str:
    """The `### ` heading text for a command: `Command: name (aliases)`."""
    name = f'`{cmd.name}`'
    if cmd.aliases:
        return f'Command: {name} (' + ', '.join(f'`{a}`' for a in cmd.aliases) + ')'
    return f'Command: {name}'


def _fragment(cmd: Command) -> str:
    """The heading-derived anchor a catalogue link should target.

    Slugs the command's index heading the way GitHub / VS Code do — drop
    inline-code backticks, lowercase, remove characters that are not
    alphanumeric / space / hyphen, then convert **each** remaining space to a
    hyphen. Punctuation removed from *between* two spaces therefore leaves a
    double hyphen, matching the renderer exactly: `Command: `!` (`sh`, `bash`)`
    → `command--sh-bash`, `Command: `?` (`help`)` → `command--help`,
    `Command: `evaluate` (`eval`)` → `command-evaluate-eval`. Heading-derived
    anchors resolve in every Markdown tool (no explicit `<a id>` needed).
    """
    text = _heading_text(cmd).replace('`', '').lower()
    return re.sub(r'[^a-z0-9 -]+', '', text).strip(' ').replace(' ', '-').strip('-')


def _usage_block(cmd: Command) -> str:
    """Render a command's usage as a fenced block (tabs flattened to spaces)."""
    lines = [ln.replace('\t', '').rstrip() for ln in cmd.usage.splitlines() if ln.strip()]
    return '```\n' + '\n'.join(lines) + '\n```'


def _docstring(cmd: Command) -> str:
    """The wrapped function's cleaned docstring (decorators unwrapped), or ''."""
    func = cmd.func
    while hasattr(func, '__wrapped__'):
        func = func.__wrapped__
    return inspect.getdoc(func) or ''


def _csv_flags(path: Path, key_col: str, flag_cols: tuple[str, ...]) -> dict[str, tuple[bool, ...]]:
    """Read *path* into ``{key → (bool per flag_col)}`` (truthy cells → True)."""
    out: dict[str, tuple[bool, ...]] = {}
    for row in csv.DictReader(path.read_text(encoding='utf-8').splitlines()):
        key = (row.get(key_col) or '').strip()
        if key:
            out[key] = tuple((row.get(col) or '').strip().lower() in _TRUTHY for col in flag_cols)
    return out


def _command_module(cmd: Command) -> str:
    """The dotted module that defines *cmd* (unwrapping the register/command decorators)."""
    func = cmd.func
    while hasattr(func, '__wrapped__'):
        func = func.__wrapped__
    return getattr(func, '__module__', '')


def _availability(cmd: Command, channels: dict[str, tuple[bool, ...]],
                  profiles: dict[str, tuple[bool, ...]]) -> str:
    """A one-line `channels: … · profiles: …` availability note for *cmd*.

    Channels come from the command's module row in ``modules.csv`` (terminal / web);
    profiles from its row in ``commands.csv`` (admin / user / guest, admin-only when
    the command is absent, matching the runtime fail-safe default).
    """
    term, web = channels.get(_command_module(cmd), (True, True))
    chans = [name for name, on in (('terminal', term), ('web', web)) if on] or ['none']
    granted = profiles.get(cmd.name)
    if granted is None:
        allowed = ['admin']
    else:
        allowed = [name for name, on in zip(_PROFILES, granted) if on] or ['none']
    return f'* channels: {", ".join(chans)} · profiles: {", ".join(allowed)}'


def _command_table(link_prefix: str) -> str:
    """A compact `Command | Aliases | Description` table; names link to the index.

    *link_prefix* is prepended to each command's anchor — `commands-index.md#`
    when the table lives in another file, `#` when it lives in the index itself.
    """
    rows = ['| Command | Aliases | Description |', '|---------|---------|-------------|']
    for cmd in registry.all():
        description, glyphs = _clean_help(cmd.help)
        suffix = (' ' + ' '.join(glyphs)) if glyphs else ''
        link = f'[`{cmd.name}`]({link_prefix}{_fragment(cmd)})'
        rows.append(f'| {link} | {_aliases(cmd)} | {description}{suffix} |')
    legend = '\n*Legend: ' + ' · '.join(f'{g} {desc}' for g, desc in _LEGEND.items()) + '.*'
    return '\n'.join(rows) + '\n' + legend


def gen_command_table() -> str:
    """Catalogue table for the user guide; names link into the command index."""
    return _command_table('commands-index.md#')


def gen_command_summary() -> str:
    """Catalogue table for the command index itself; names link to same-file anchors."""
    return _command_table('#')


def gen_command_index() -> str:
    """A per-command reference (heading, flags, availability, usage, docstring), rule-separated."""
    channels = _csv_flags(config.modules_file, 'module', ('terminal', 'web'))
    profiles = _csv_flags(config.commands_file, 'command', _PROFILES)
    sections: list[str] = []
    for cmd in registry.all():
        description, glyphs = _clean_help(cmd.help)
        parts = [f'#### {_heading_text(cmd)}', '']
        if description:
            parts += [description]
        availability = [_availability(cmd, channels, profiles)]
        if glyphs:
            availability += [f'* {g} {_LEGEND[g]}' for g in glyphs]
        parts += ['\n'.join(availability)]
        parts += ['']
        parts.append(_usage_block(cmd))
        docstring = _docstring(cmd)
        if docstring:
            parts += ['', '```text', docstring, '```']
        sections.append('\n'.join(parts))
    return '\n\n---\n\n'.join(sections)


#: The package whose module tree is rendered into the README package-layout block.
_PACKAGE = 'solver'

#: Source-file suffixes listed in the package layout.
_SOURCE_SUFFIXES = ('.py', '.c', '.h')


def _module_summary(path: Path) -> str:
    """First docstring / header-comment line of *path*, or '' if absent / unparseable.

    For `.py` the module docstring; for `.c` / `.h` the first non-empty line of the
    leading `/* … */` block comment.
    """
    text = path.read_text()
    if path.suffix == '.py':
        try:
            doc = ast.get_docstring(ast.parse(text))
        except (SyntaxError, ValueError):
            return ''
        return doc.strip().splitlines()[0].strip() if doc else ''
    if (match := re.search(r'/\*+(.*?)\*/', text, re.DOTALL)) is None:
        return ''
    for line in match.group(1).splitlines():
        if stripped := line.strip().lstrip('*').strip():
            return stripped
    return ''


def _is_source(path: Path) -> bool:
    """True for a non-empty `.py`/`.c`/`.h` file (suffix checked before reading)."""
    return path.is_file() and path.suffix in _SOURCE_SUFFIXES and bool(path.read_text().strip())


def _layout_rows(directory: Path, depth: int, rows: list[tuple[str, str]]) -> None:
    """Append `(left, summary)` rows for *directory* — its non-empty source files, then subpackages.

    `__init__.py` is not listed as a file; a package's `__init__.py` docstring (when non-empty)
    becomes the summary on the directory's own row instead.
    """
    indent = '  ' * depth
    for f in sorted(p for p in directory.iterdir() if p.name != '__init__.py' and _is_source(p)):
        rows.append((f'{indent}{f.name}', _module_summary(f)))
    for d in sorted(p for p in directory.iterdir() if p.is_dir() and p.name != '__pycache__'):
        if not any(_is_source(p) for p in d.rglob('*')):
            continue  # skip directories with no source files (e.g. the claude/ config tree)
        init = d / '__init__.py'
        summary = _module_summary(init) if init.exists() and _is_source(init) else ''
        rows.append((f'{indent}{d.name}/', summary))
        _layout_rows(d, depth + 1, rows)


def gen_package_layout() -> str:
    """A fenced tree of the `solver` package's non-empty source files and their docstring summaries."""
    pkg = config.root_dir / _PACKAGE
    init = pkg / '__init__.py'
    rows: list[tuple[str, str]] = [(f'{_PACKAGE}/', _module_summary(init) if _is_source(init) else '')]
    _layout_rows(pkg, 1, rows)
    width = max(len(left) for left, summary in rows if summary)
    lines = [f'{left:<{width}} — {summary}' if summary else left for left, summary in rows]
    return '```\n' + '\n'.join(lines) + '\n```'


#: Marker name → generator producing the block body (no surrounding markers).
GENERATORS: dict[str, Callable[[], str]] = {
    'command-table': gen_command_table,
    'command-summary': gen_command_summary,
    'command-index': gen_command_index,
    'package-layout': gen_package_layout,
}


def _block_re(name: str) -> re.Pattern[str]:
    """Match a `<!-- GEN:name -->` … `<!-- /GEN:name -->` block (body in between)."""
    return re.compile(
        rf'(<!-- GEN:{re.escape(name)} -->).*?(<!-- /GEN:{re.escape(name)} -->)',
        re.DOTALL,
    )


def _render(text: str) -> tuple[str, list[str]]:
    """Rewrite every known GEN block in *text*; return *(new_text, changed_names)*."""
    changed: list[str] = []
    for name, generator in GENERATORS.items():
        pattern = _block_re(name)
        if not pattern.search(text):
            continue
        body = generator()

        def _sub(match: re.Match[str]) -> str:
            return f'{match.group(1)}\n{body}\n{match.group(2)}'

        new_text = pattern.sub(_sub, text)
        if new_text != text:
            changed.append(name)
            text = new_text
    return text, changed


#: Per-profile cells a brand-new command gets in commands.csv (admin + user, not guest).
_DEFAULT_COMMAND_POLICY: tuple[str, str, str] = ('True', 'True', '')


def _sync_commands(check: bool) -> str | None:
    """Reconcile ``solver/commands.csv`` with the live command registry.

    Mirrors :func:`solver.utils.loader.update_modules` for the authorization policy:
    the row set follows ``registry.all()`` (new commands appended with the default
    :data:`_DEFAULT_COMMAND_POLICY`, removed commands dropped), while every existing
    row's ``admin``/``user``/``guest`` cells are **preserved verbatim** so manual
    grants survive. Returns a ``file: reason`` entry when the file (would) change,
    else None; with *check* True nothing is written.

    Guarded to the ``admin`` profile — the only one whose registry holds every
    command — so it never prunes commands merely hidden from a lesser profile.
    ``update-docs`` is admin- and terminal-only, so this always holds in practice.
    """
    if config.user_profile != 'admin':
        return None
    existing: dict[str, tuple[str, str, str]] = {}
    if config.commands_file.exists():
        with open(config.commands_file, newline='') as handle:
            existing = {row[0]: (row[1], row[2], row[3]) for row in csv.reader(handle) if len(row) == 4}

    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator='\n')
    writer.writerow(['command', *_PROFILES])
    for cmd in registry.all():
        writer.writerow([cmd.name, *existing.get(cmd.name, _DEFAULT_COMMAND_POLICY)])
    new_text = buffer.getvalue()

    old_text = config.commands_file.read_text(encoding='utf-8') if config.commands_file.exists() else ''
    if new_text == old_text:
        return None
    if not check:
        config.commands_file.write_text(new_text, encoding='utf-8')
    try:
        label = str(config.commands_file.relative_to(ROOT))
    except ValueError:
        label = config.commands_file.name
    return f'{label}: command policy'


def _apply(check: bool) -> tuple[list[str], list[str]]:
    """Render every doc; return *(updated, stale)* as `<file>: <blocks>` strings.

    With *check* False, out-of-date docs are written and listed in *updated*;
    with *check* True nothing is written and they are listed in *stale* instead.
    """
    updated: list[str] = []
    stale: list[str] = []
    targets = sorted(DOCS_DIR.glob('*.md')) + [ROOT / 'README.md', ROOT / 'CLAUDE.md']
    for doc in targets:
        original = doc.read_text()
        rendered, changed = _render(original)
        if not changed or rendered == original:
            continue
        entry = f'{doc.relative_to(ROOT)}: {", ".join(changed)}'
        if check:
            stale.append(entry)
        else:
            doc.write_text(rendered)
            updated.append(entry)
    return updated, stale


@register(help_text='Regenerate the generated sections of the docs/ guides.', pass_ctx=True, quietable=True)
def update_docs(ctx: Context, check: bool = False) -> int:
    """Rebuild the registry-generated blocks in the `docs/` guides and the README.

    Rewrites only the marked `<!-- GEN:... -->` sections — the command catalogue,
    the in-index summary, the per-command reference, and the README package-layout
    tree (built from each module's docstring) — from the live command registry and
    the source tree, leaving all hand-written prose untouched. It also reconciles
    the authorization policy `solver/commands.csv` with the registry (new commands
    added with the default admin+user grant, removed ones dropped, existing grants
    preserved) — the counterpart to `modules.csv`. Run it after changing any
    command's name, alias, help text, or signature, or a module's first docstring
    line.

    Args:
        ctx:    The command context.
        check:  When True, write nothing and fail (non-zero) if any doc is out
                of date, listing the stale files. When False (default), rewrite
                the docs in place and report which were updated.
    """
    profile = ctx.shell.profile
    if update_modules(profile):
        load_commands(profile)
        console.print('[success]modules updated[/success]')
    else:
        console.print('[muted]modules already up to date[/muted]')
    command_entry = _sync_commands(check)   # keep commands.csv in step with the registry first
    updated, stale = _apply(check)
    if command_entry:
        (stale if check else updated).insert(0, command_entry)
    if check:
        if stale:
            console.print('[error]docs out of date[/error] (run [accent]update-docs[/accent]):')
            for entry in stale:
                console.print(f'  [warning]{entry}[/warning]')
            return ExitCodes.EXIT_ERROR
        console.print('[success]docs are up to date[/success]')
        return ExitCodes.EXIT_OK
    if updated:
        for entry in updated:
            console.print(f'[success]updated[/success] {entry}')
    else:
        console.print('[muted]docs already up to date[/muted]')
    return ExitCodes.EXIT_OK

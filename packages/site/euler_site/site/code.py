#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The code viewer: the project's own source, browsable on the public site at `/code/`.

docs/web-server-guide.md § The code viewer. The scope is :data:`content.CODE_ROOTS` — the
three packages and the content wheel, `scripts/`, and the root files that configure them —
as the content wheel ships them (`scripts/content/stage.py`), so what the page shows is the
code of the last deploy, the same for every reader. Nothing here reads a clone.

Two reads, each cached for the life of the process (the tree changes only with a redeploy,
which restarts it):

- :func:`index` walks the scope once into a :class:`Node` tree, each file and folder with
  its **summary**: the first sentence of what the file says about itself (its docstring, its
  header comment, its heading — :func:`summary`), which the page sets as its headline and
  the tree offers on hover and to the filter.
- :func:`highlight` renders one file through Pygments into numbered lines, each its own
  `#L<n>` anchor. A file too large or too long-lined to colour (the minified vendor bundles)
  is shown plain; one that is not text is offered raw.
"""
from __future__ import annotations

__all__ = ['Node', 'Listing', 'index', 'find', 'summary', 'highlight', 'ticks', 'plain', 'MAX_SHOWN']

import ast
import re
import tomllib
from dataclasses import dataclass, field
from functools import cache
from html import escape
from pathlib import Path

from markupsafe import Markup
from pygments import highlight as _pygmentize
from pygments.formatters import HtmlFormatter
from pygments.lexer import Lexer
from pygments.lexers import TextLexer, get_lexer_by_name, get_lexer_for_filename
from pygments.util import ClassNotFound

from euler_site.site.content import CODE_ROOTS

#: Larger than this, a file is not shown at all — only offered raw (the MathJax bundle).
MAX_SHOWN: int = 512 * 1024
#: Larger than this, or with a line longer than :data:`_MAX_LINE`, a file is shown uncoloured:
#: Pygments on a minified bundle costs seconds and buys nothing anyone reads.
_MAX_COLOURED: int = 160 * 1024
_MAX_LINE: int = 1000
#: Longest summary kept: a first sentence that runs past this is a paragraph, cut at a word.
_MAX_SUMMARY: int = 220

#: Lexers by file name or suffix, where Pygments has none or picks the wrong one. The hook
#: templates are shell with a placeholder; the git and ShellCheck dotfiles are comment-led
#: lists that read best as shell or INI.
_LEXERS: dict[str, str] = {
    '.template': 'bash', '.gitattributes': 'bash', '.gitignore': 'bash', '.allow': 'bash',
    '.shellcheckrc': 'ini', '.conf': 'ini', '.html': 'html+jinja',
}
#: The language a reader would name, where the lexer's own name is not it.
_LANGUAGES: dict[str, str] = {'HTML+Django/Jinja': 'HTML', 'Text only': 'text', 'Bash': 'Bash'}
#: Leading lines that are not the file's description: a shebang, an encoding cookie, a
#: ShellCheck directive, and a template's `{% extends %}` / `{% block %}` openers.
_PREAMBLE_RE = re.compile(r'#!|#\s*-\*-|#\s*shellcheck\b|\{%-?\s*(?:extends|block|import|from)\b')
#: A banner rule under a title (`# =====`): the end of the paragraph, not part of it.
_RULE_RE = re.compile(r'[=\-─━_*#~]{3,}')
#: A sentence end: `.`/`!`/`?` before whitespace — so `solver.config` does not end one — and
#: not after the abbreviations a description uses mid-sentence.
_SENTENCE_RE = re.compile(r'^(.+?(?<!\be\.g)(?<!\bi\.e)(?<!\betc)(?<!\bvs)(?<!\bcf)[.!?])(?=\s|$)', re.DOTALL)
#: A parenthetical that points at a document (`(docs/package-guide.md § 1)`): a reference for
#: the source's reader, noise in a headline.
_DOC_REF_RE = re.compile(r'\s*\([^()]*(?:\.md|§)[^()]*\)')
#: Sphinx roles and reST emphasis, which a headline shows as their text.
_ROLE_RE = re.compile(r':\w+:`~?([^`]+)`')
_SKIPPED: frozenset[str] = frozenset({'__pycache__', 'build', 'dist'})
#: A backticked span in a summary: code, in the source's own convention.
_TICKS_RE = re.compile(r'`([^`]+)`')


@dataclass
class Node:
    """One file or folder in the scope: repo-relative *path* (a folder's ends `/`)."""

    name: str
    path: str
    is_dir: bool
    summary: str | None = None
    children: list[Node] = field(default_factory=list)

    @property
    def files(self) -> int:
        """How many files sit under this node (1 for a file)."""
        return 1 if not self.is_dir else sum(child.files for child in self.children)


@dataclass(frozen=True)
class Listing:
    """One file, rendered: its lines (HTML, one per source line), language, and how shown."""

    lines: list[str]
    language: str
    size: int
    coloured: bool
    text: bool


def summary(path: Path) -> str | None:
    """The first sentence *path* says about itself, as plain text — or None.

    A Python module's docstring, a Markdown file's first heading, a `pyproject.toml`'s
    `description`, and otherwise the file's leading comment block (`#`, `//`, `/* … */`,
    `{# … #}`, `<!-- … -->`), after any shebang and encoding line. Only the first paragraph
    counts, and of that the first sentence, without the document references it cites.
    """
    try:
        text = path.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError):
        return None
    paragraph: str | None
    if path.suffix == '.py':
        paragraph = _docstring(text) or _comment(text)
    elif path.suffix == '.md':
        paragraph = next((line[2:] for line in text.splitlines() if line.startswith('# ')), None)
    elif path.name == 'pyproject.toml':
        paragraph = _description(text) or _comment(text)
    elif path.name == 'LICENSE':
        paragraph = next((line for line in text.splitlines() if line.strip()), None)
    else:
        paragraph = _comment(text)
    return _first_sentence(paragraph) if paragraph else None


def ticks(text: str | None) -> Markup:
    """A summary as HTML for the page: escaped, its backticked spans set as `<code>`."""
    return Markup(_TICKS_RE.sub(r'<code>\1</code>', escape(text or '', quote=False)))


def plain(text: str | None) -> str:
    """A summary as plain text, for an attribute: the backticks dropped."""
    return (text or '').replace('`', '')


def _docstring(text: str) -> str | None:
    try:
        doc = ast.get_docstring(ast.parse(text))
    except (SyntaxError, ValueError):
        return None
    return doc.split('\n\n', 1)[0] if doc else None


def _description(text: str) -> str | None:
    try:
        value = tomllib.loads(text).get('project', {}).get('description')
    except tomllib.TOMLDecodeError:
        return None
    return value if isinstance(value, str) else None


def _comment(text: str) -> str | None:
    """The first paragraph of the file's leading comment block, markers stripped."""
    lines = text.splitlines()
    while lines and (not lines[0].strip() or _PREAMBLE_RE.match(lines[0])):
        lines.pop(0)
    if not lines:
        return None
    first = lines[0].lstrip()
    for opener, closer in (('/*', '*/'), ('{#', '#}'), ('<!--', '-->')):
        if first.startswith(opener):
            block = '\n'.join(lines).lstrip()[len(opener):].split(closer, 1)[0]
            body = [line.strip().lstrip('*').strip() for line in block.splitlines()]
            return _paragraph(body)
    for marker in ('#', '//', ';'):
        if first.startswith(marker):
            body = []
            for line in lines:
                stripped = line.strip()
                if not stripped.startswith(marker):
                    break
                body.append(stripped[len(marker):].strip())
            return _paragraph(body)
    return None


def _paragraph(lines: list[str]) -> str | None:
    """The leading run of non-blank *lines*, joined — the paragraph a description opens with."""
    while lines and not lines[0]:
        lines.pop(0)
    out = []
    for line in lines:
        if not line or _RULE_RE.fullmatch(line):
            break
        out.append(line)
        if line.endswith(':'):          # what follows is a list, not more of the sentence
            break
    return ' '.join(out) or None


def _first_sentence(paragraph: str) -> str:
    text = ' '.join(paragraph.split())
    text = _ROLE_RE.sub(r'\1', text).replace('**', '')
    match = _SENTENCE_RE.match(text)
    sentence = match.group(1) if match else text
    sentence = _DOC_REF_RE.sub('', sentence).strip()
    if sentence.endswith(':'):
        sentence = sentence[:-1].rstrip() + '.'
    if len(sentence) > _MAX_SUMMARY:
        sentence = sentence[:_MAX_SUMMARY].rsplit(' ', 1)[0] + '…'
    return sentence


@cache
def index(root: Path) -> Node:
    """The scope under *root* (a content tree or a clone) as a tree, folders first, A→Z."""
    top = Node(name='', path='', is_dir=True)
    for scope in CODE_ROOTS:
        target = root / scope
        if scope.endswith('/'):
            if target.is_dir():
                top.children.append(_walk(root, target))
        elif target.is_file():
            top.children.append(Node(name=target.name, path=scope, is_dir=False, summary=summary(target)))
    _sort(top)
    return top


def _walk(root: Path, folder: Path) -> Node:
    rel = folder.relative_to(root).as_posix() + '/'
    node = Node(name=folder.name, path=rel, is_dir=True)
    for entry in folder.iterdir():
        if entry.name in _SKIPPED or entry.name.endswith('.egg-info') or entry.is_symlink():
            continue
        if entry.is_dir():
            node.children.append(_walk(root, entry))
        elif entry.is_file():
            node.children.append(Node(name=entry.name, path=f'{rel}{entry.name}', is_dir=False,
                                      summary=summary(entry)))
    node.summary = _folder_summary(folder, node)
    return node


def _folder_summary(folder: Path, node: Node) -> str | None:
    """A folder speaks through its `__init__.py`, its `pyproject.toml`, or its `README.md`."""
    by_name = {child.name: child for child in node.children}
    for name in ('__init__.py', 'pyproject.toml', 'README.md'):
        child = by_name.get(name)
        if child is not None and child.summary:
            return child.summary
    return None


def _sort(node: Node) -> None:
    node.children.sort(key=lambda child: (not child.is_dir, child.name.lower()))
    for child in node.children:
        if child.is_dir:
            _sort(child)


def find(root: Path, path: str) -> list[Node] | None:
    """The chain of nodes from the top to *path* (a file, or a folder ending `/`), or None."""
    chain = [index(root)]
    parts = [part for part in path.split('/') if part]
    for i, part in enumerate(parts):
        last = i == len(parts) - 1
        want_dir = not last or path.endswith('/')
        step = next((child for child in chain[-1].children
                     if child.name == part and (child.is_dir or not want_dir)), None)
        if step is None:
            return None
        chain.append(step)
    return chain


def _lexer(path: Path, text: str) -> Lexer:
    name = _LEXERS.get(path.name) or _LEXERS.get(path.suffix)
    # stripnl off: by default a lexer drops leading and trailing blank lines, which would
    # number every line after them wrongly.
    if name:
        return get_lexer_by_name(name, stripnl=False)
    try:
        return get_lexer_for_filename(path.name, text, stripnl=False)
    except ClassNotFound:
        return TextLexer(stripnl=False)


@cache
def highlight(path: Path) -> Listing:
    """*path* as numbered lines of HTML: coloured by Pygments, or plain when too big to colour."""
    size = path.stat().st_size
    if size > MAX_SHOWN:
        return Listing(lines=[], language='', size=size, coloured=False, text=False)
    try:
        text = path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        return Listing(lines=[], language='', size=size, coloured=False, text=False)
    lexer = _lexer(path, text)
    language = _LANGUAGES.get(lexer.name, lexer.name)
    source = text[:-1] if text.endswith('\n') else text
    if size > _MAX_COLOURED or any(len(line) > _MAX_LINE for line in source.split('\n')):
        return Listing(lines=[escape(line) for line in source.split('\n')], language=language,
                       size=size, coloured=False, text=True)
    # nowrap: bare spans, which the formatter closes at every line end — so the output
    # splits into lines that each stand alone, ready to be numbered and anchored.
    # Lexed with exactly one final newline (the lexer would add it, ensurenl), which ends
    # the last line rather than starting another — so it is the one newline taken off.
    rendered = _pygmentize(source + '\n', lexer, HtmlFormatter(nowrap=True)).removesuffix('\n')
    return Listing(lines=rendered.split('\n'), language=language, size=size,
                   coloured=True, text=True)

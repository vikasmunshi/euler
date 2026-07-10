#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Config-free readers for the content trees the service renders (Phase 5b).

Every function takes the repo working tree (``SiteConfig.repo_root``) explicitly
and imports nothing from :mod:`solver.config` (which resolves the shell's
identity + per-user state — paths the service uid cannot use, DD-12). The
service reads exactly the DD-12 content-ACL trees — ``solutions/`` · ``docs/`` ·
``topics/`` · ``solver/web/content/`` — plus, best-effort, the AI reference
sources under ``solver/`` for the composed ``ai`` doc, which degrade to a note
when the uid may not read them.
"""
from __future__ import annotations

__all__ = ['ProblemInfo', 'Century', 'DocEntry', 'TEXT_SUFFIXES',
           'solution_dir', 'load_problems', 'centuries', 'problem_files',
           'resolve_file', 'load_json', 'render_markdown',
           'list_docs', 'read_doc', 'list_topics', 'read_topic']

import json
import mimetypes
import re
from pathlib import Path
from typing import Any, NamedTuple

from markdown_it import MarkdownIt

#: Markdown renderer for the guides/topics (GitHub-flavoured: tables + strikethrough).
_MD = MarkdownIt('commonmark').enable(['table', 'strikethrough'])

#: Suffixes the file view renders inline as escaped source; anything else
#: (images, downloads) is served as raw bytes.
TEXT_SUFFIXES: frozenset[str] = frozenset({'.py', '.c', '.h', '.json', '.html', '.md', '.txt', '.csv'})

#: A doc/topic page name: a bare stem, no separators (anything else is 404).
_NAME_RE = re.compile(r'[\w-]+')


class ProblemInfo(NamedTuple):
    """One row of ``problems.json``: the scraped progress-page metadata."""

    number: int
    title: str
    level: int | None
    pct: int | None
    solved: bool
    date: str

    @property
    def heat(self) -> int:
        """Difficulty bucket 1–5 (by ``pct``) shading a solved cell in the grid."""
        if not self.pct:
            return 1
        return 1 + min((self.pct - 1) // 20, 4)


class Century(NamedTuple):
    """One 10×10 grid: problems ``start`` … ``start+99`` (missing numbers → None)."""

    start: int
    cells: list[ProblemInfo | None]
    solved: int


class DocEntry(NamedTuple):
    """A docs/topics index row: the URL name and the page's leading title."""

    name: str
    title: str


# ── solutions ────────────────────────────────────────────────────────────────────────

def solution_dir(repo_root: Path, number: int) -> Path:
    """The problem's on-disk directory (mirrors :func:`solver.core.problems.solution_dir`)."""
    if number > 100:
        start = number // 100 * 100
        return repo_root / 'solutions' / 'private' / f'p{start:04d}_{start + 99:04d}' / f'p{number:04d}'
    return repo_root / 'solutions' / 'public' / f'p{number:04d}'


#: mtime-keyed cache of the parsed problems.json, per path.
_problems_cache: dict[Path, tuple[float, dict[int, ProblemInfo]]] = {}


def load_problems(repo_root: Path) -> dict[int, ProblemInfo]:
    """The parsed ``solutions/problems.json``, cached until the file's mtime moves."""
    path = repo_root / 'solutions' / 'problems.json'
    try:
        mtime = path.stat().st_mtime
    except OSError:
        return {}
    cached = _problems_cache.get(path)
    if cached is not None and cached[0] == mtime:
        return cached[1]
    try:
        raw: dict[str, dict[str, Any]] = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return {}
    problems = {
        int(num): ProblemInfo(
            number=int(num),
            title=str(info.get('title', '')),
            level=info['level'] if isinstance(info.get('level'), int) else None,
            pct=info['pct'] if isinstance(info.get('pct'), int) else None,
            solved=bool(info.get('solved')),
            date=str(info.get('date', '')),
        )
        for num, info in raw.items() if str(num).isdigit()
    }
    _problems_cache[path] = (mtime, problems)
    return problems


def centuries(problems: dict[int, ProblemInfo]) -> list[Century]:
    """The 10×10 century grids covering problems 1 … the highest known number."""
    if not problems:
        return []
    top = max(problems)
    grids: list[Century] = []
    for start in range(1, top + 1, 100):
        cells = [problems.get(n) for n in range(start, start + 100)]
        grids.append(Century(start=start, cells=cells,
                             solved=sum(1 for c in cells if c is not None and c.solved)))
    return grids


def problem_files(sdir: Path) -> list[str]:
    """The problem's viewable files (mimetype-guessable, as ``ls`` lists them),
    as POSIX paths relative to the solution directory."""
    if not sdir.is_dir():
        return []
    return sorted(
        p.relative_to(sdir).as_posix() for p in sdir.rglob('*')
        if p.is_file() and mimetypes.guess_type(p.name)[0] is not None
    )


def resolve_file(sdir: Path, filename: str) -> Path | None:
    """Resolve *filename* inside *sdir*, or None — rejects traversal and symlink escape."""
    relative = Path(filename)
    if relative.is_absolute() or '..' in relative.parts:
        return None
    target = sdir / relative
    try:
        if not target.resolve().is_relative_to(sdir.resolve()):
            return None
    except OSError:
        return None
    return target if target.is_file() else None


def load_json(path: Path) -> Any | None:
    """Parse a JSON file, or None when it is missing or malformed."""
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None


# ── markdown (docs + topics) ────────────────────────────────────────────────────────

def _doc_slug(text: str) -> str:
    """GitHub-style heading slug — matches `update_doc.py`'s catalogue anchors, so a
    guide's `commands-index.md#command-…` links resolve to the rendered headings."""
    return re.sub(r'[^a-z0-9 -]+', '', text.lower()).strip(' ').replace(' ', '-').strip('-')


def render_markdown(text: str, route_base: str = '/docs/') -> str:
    """Render Markdown to HTML: slugged heading ids + `.md` cross-links rewired.

    Each heading gets the same slug `update_doc.py` assumes, so in-page and
    cross-doc `#anchor` links land; a relative `foo.md` (or `docs/foo.md`) link is
    rewritten to the *route_base* route.
    """
    tokens = _MD.parse(text)
    for i, token in enumerate(tokens):
        if token.type == 'heading_open':
            token.attrSet('id', _doc_slug(tokens[i + 1].content))
    rendered: str = _MD.renderer.render(tokens, _MD.options, {})
    return re.sub(r'href="(?:docs/)?([\w-]+)\.md(#[^"]*)?"', rf'href="{route_base}\1\2"', rendered)


def _page_title(text: str, fallback: str) -> str:
    """The page's leading `# ` heading, or *fallback*."""
    for line in text.splitlines():
        if line.startswith('# '):
            return line[2:].strip()
    return fallback


def _list_pages(tree: Path) -> list[DocEntry]:
    """Index the `*.md` pages of a content tree by name + leading title."""
    if not tree.is_dir():
        return []
    entries = []
    for path in sorted(tree.glob('*.md')):
        try:
            text = path.read_text(encoding='utf-8')
        except OSError:
            continue
        entries.append(DocEntry(name=path.stem, title=_page_title(text, path.stem)))
    return entries


def _read_page(tree: Path, name: str) -> str | None:
    """The raw Markdown of one page of a content tree, or None (bad name / missing)."""
    if name.endswith('.md'):                       # a rewritten cross-link that kept its suffix
        name = name[:-3]
    if not _NAME_RE.fullmatch(name):
        return None
    try:
        return (tree / f'{name}.md').read_text(encoding='utf-8')
    except OSError:
        return None


# ── docs ────────────────────────────────────────────────────────────────────────────

#: The AI reference sources composed into the `ai` doc. They live under `solver/`
#: — outside the content ACLs — so each is read best-effort (see `_ai_section`).
_AI_SKILL_MD = 'solver/ai/claude/skills/claude-euler-solver/SKILL.md'
_AI_PROMPTS_DIR = 'solver/templates'

_AI_INTRO = """\
# AI reference

The framework's two AI paths, collated into one reference. The shell's
`claude-skill` command runs Claude Code **headless** against a single problem's
solution files (the **claude-euler-solver** skill, below); `claude-api` generates
solution artifacts — Python and C code, `notes.html`, `test_cases.json` — through
the Claude API from the **prompt templates** below. Both are held to the shared
`convention_*` guides listed in the [docs index](/docs/).
"""


def _strip_frontmatter(text: str) -> str:
    """Drop a leading YAML front-matter block so it does not render as body text."""
    return re.sub(r'\A---\n.*?\n---\n', '', text, count=1, flags=re.DOTALL)


def _fence(content: str) -> str:
    """Wrap *content* in a `text` code fence long enough to survive backticks inside it."""
    longest = max((len(run) for run in re.findall(r'`+', content)), default=0)
    ticks = '`' * max(3, longest + 1)
    return f'{ticks}text\n{content}\n{ticks}'


def _ai_section(heading: str, path: Path, body: str) -> str:
    """One composed section, or a muted note when the source is unreadable.

    The sources live under ``solver/`` — outside the DD-12 content ACLs — so a
    deployed per-profile uid may lack read on them; the page degrades rather
    than 500s (in a dev run as the owner it renders in full).
    """
    if body:
        return f'{heading}\n\n{body}'
    return f'{heading}\n\n*`{path.as_posix()}` is not readable by this service.*'


def _compose_ai_doc(repo_root: Path) -> str:
    """The `ai` doc's Markdown: intro + the skill definition + the prompt templates."""
    sections = [_AI_INTRO]
    skill = repo_root / _AI_SKILL_MD
    try:
        skill_body = _strip_frontmatter(skill.read_text(encoding='utf-8'))
    except OSError:
        skill_body = ''
    sections.append(_ai_section('## The claude-euler-solver skill',
                                skill.relative_to(repo_root), skill_body))
    prompts_dir = repo_root / _AI_PROMPTS_DIR
    try:
        prompts = sorted(prompts_dir.glob('prompt_*.txt'))
    except OSError:
        prompts = []
    if prompts:
        for path in prompts:
            try:
                body = f'### `{path.name}`\n\n' + _fence(path.read_text(encoding='utf-8').strip())
            except OSError:
                body = ''
            sections.append(_ai_section('', path.relative_to(repo_root), body).strip())
    else:
        sections.append(_ai_section('## The claude-api prompt templates',
                                    Path(_AI_PROMPTS_DIR), ''))
    return '\n\n---\n\n'.join(section.strip() for section in sections)


def list_docs(repo_root: Path) -> list[DocEntry]:
    """The docs index: every `docs/*.md` guide plus the composed `ai` reference."""
    entries = _list_pages(repo_root / 'docs')
    entries.append(DocEntry(name='ai', title='AI reference'))
    return sorted(entries)


def read_doc(repo_root: Path, name: str) -> str | None:
    """The raw Markdown of `/docs/{name}`: a `docs/` guide, or the composed `ai` page."""
    if name in ('ai', 'ai.md'):
        return _compose_ai_doc(repo_root)
    return _read_page(repo_root / 'docs', name)


# ── topics ──────────────────────────────────────────────────────────────────────────

def list_topics(repo_root: Path) -> list[DocEntry]:
    """The topics index: every `topics/*.md` writeup."""
    return _list_pages(repo_root / 'topics')


def read_topic(repo_root: Path, name: str) -> str | None:
    """The raw Markdown of `/topics/{name}`."""
    return _read_page(repo_root / 'topics', name)

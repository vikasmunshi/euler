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

__all__ = ['ProblemInfo', 'Century', 'DocEntry', 'TEXT_SUFFIXES', 'ABOUT_PAGES',
           'solution_dir', 'load_problems', 'centuries', 'problem_files',
           'resolve_file', 'resolve_repo_file', 'load_json', 'render_markdown', 'git_status',
           'list_docs', 'read_doc', 'list_topics', 'read_topic', 'read_about',
           'parse_progress', 'save_progress']

import json
import mimetypes
import re
import subprocess
from pathlib import Path
from typing import Any, NamedTuple

from bs4 import BeautifulSoup, Tag
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
    """A docs/topics index row (site-design §7): the URL *name*, the *heading*
    derived from the filename (title-cased, separators → spaces — the card's
    first line), and the *title* from the page's leading ``#`` heading (second
    line). Index lists are sorted by *name* (the filename)."""

    name: str
    heading: str
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
    as POSIX paths relative to the solution directory. **Zero-size files are
    hidden** (site-design §7) — an empty stub says nothing worth a link."""
    if not sdir.is_dir():
        return []
    return sorted(
        p.relative_to(sdir).as_posix() for p in sdir.rglob('*')
        if p.is_file() and p.stat().st_size > 0
        and mimetypes.guess_type(p.name)[0] is not None
    )


def git_status(repo_root: Path, sdir: Path) -> dict[str, tuple[str, str]]:
    """Best-effort git status for *sdir*: relative name → (css class, hover title).

    Read-only, and the *only* git the web tier runs (DD-12: no commits, no
    checkouts, no key). It works from the deployed per-profile uids because
    ``.git`` is world-readable and the query carries its own
    ``safe.directory`` exception: git otherwise **refuses a repository owned by
    another uid** ("detected dubious ownership") — that ownership check, not the
    file permissions, is what would silence the status colours on a deployed
    instance. ``-c`` is *protected* configuration scope (like system/global), so
    the exception is honoured; it is scoped to this one invocation rather than
    written into the host's git config, so no other process or uid gains
    anything.

    Any failure still degrades to ``{}`` (files render plain) — a missing git
    binary, a repo-less deployment, a timeout. A name absent from the porcelain
    output is clean/committed.
    """
    try:
        proc = subprocess.run(
            ['git', '-C', str(repo_root), '-c', f'safe.directory={repo_root}',
             'status', '--porcelain', '--', str(sdir)],
            capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return {}
    if proc.returncode != 0:
        return {}
    states: dict[str, tuple[str, str]] = {}
    for line in proc.stdout.splitlines():
        if len(line) < 4:
            continue
        # Porcelain: X = index (staged) state, Y = worktree state, then the path.
        x, y, path = line[0], line[1], line[3:].split(' -> ')[-1].strip().strip('"')
        try:
            name = (repo_root / path).relative_to(sdir).as_posix()
        except ValueError:
            continue
        if x == '?' or y == '?':
            states[name] = ('untracked', 'untracked — not yet added to git')
        elif y != ' ':
            states[name] = ('modified', 'modified since the last commit')
        else:
            states[name] = ('staged', 'staged — not yet committed')
    return states


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


def resolve_repo_file(repo_root: Path, roots: list[str], rel: str) -> Path | None:
    """Resolve a repo-relative path to a file under one of *roots*, or None.

    *roots* are the **declared-readable** content-object paths (the ``docs`` /
    ``about`` object trees — dirs or single files); the returned file must sit
    under one of them, keeping the ``/docs/file/`` view DD-12-honest (it can only
    serve what the policy declares readable). Rejects traversal + symlink escape.
    """
    relative = Path(rel)
    if not rel or relative.is_absolute() or '..' in relative.parts:
        return None
    target = repo_root / relative
    try:
        resolved = target.resolve()
        if not resolved.is_relative_to(repo_root.resolve()):
            return None
    except OSError:
        return None
    for root in roots:
        try:
            base = (repo_root / root).resolve()
        except OSError:
            continue
        if base.is_file() and resolved == base:
            return target if target.is_file() else None
        if base.is_dir() and resolved.is_relative_to(base):
            return target if target.is_file() else None
    return None


def load_json(path: Path) -> Any | None:
    """Parse a JSON file, or None when it is missing or malformed."""
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None


# ── progress (the /edit/solutions/ collection editor, 5d) ──────────────────────────

def parse_progress(text: str) -> dict[int, dict[str, str | int | bool]]:
    """Parse a saved projecteuler.net progress page into problem metadata.

    The config-free port of ``solver.utils.summary._parse_progress_html``,
    operating on the submitted text (so a bad edit is rejected *before* anything
    lands on disk). Returns ``{number: {title, level, pct, solved, date}}`` —
    ``level``/``pct`` are ints or ``''`` when unknown, matching the shell's
    writer so the two producers of ``problems.json`` stay interchangeable.
    """
    soup = BeautifulSoup(text, 'html.parser')
    problems: dict[int, dict[str, str | int | bool]] = {}
    for td in soup.find_all('td', class_='tooltip'):
        a_tag = td.find('a', href=True)
        if not a_tag or not str(a_tag.get('href', '')).startswith('problem='):
            continue
        try:
            num = int(str(a_tag['href']).split('=')[1])
        except (ValueError, IndexError):
            continue
        # Difficulty level from CSS class t_N
        level: int | str = ''
        for cls in (td.get('class') or []):
            if cls.startswith('t_'):
                try:
                    level = int(cls[2:])
                except ValueError:
                    pass
        # Title, percentage, and completion date from tooltip span
        title: str = ''
        pct: int | str = ''
        date: str = ''
        tooltip: Tag | None = a_tag.find('span', class_='tooltiptext_narrow')
        if tooltip:
            for div in tooltip.find_all('div'):
                text_div: str = div.get_text(strip=True)
                if text_div.startswith('"') and text_div.endswith('"'):
                    title = text_div[1:-1]
                elif 'Difficulty:' in text_div and '[' in text_div:
                    try:
                        pct = int(text_div.split('[')[1].split('%')[0].strip())
                        if level == '' and 'Level' in text_div:
                            level = int(text_div.split('Level')[1].split('[')[0].strip())
                    except (ValueError, IndexError):
                        pass
                elif text_div.startswith('Completed on '):
                    date = text_div[len('Completed on '):]
        solved: bool = 'problem_solved' in (td.get('class') or [])
        problems[num] = {'title': title, 'level': level, 'pct': pct, 'solved': solved, 'date': date}
    return problems


def save_progress(repo_root: Path, content: bytes) -> tuple[bool, str]:
    """The progress save gate: parse-or-reject, then write both derived files.

    The submitted page source must parse to at least one problem (the 5c
    reject semantics — a broken paste never lands); on success it is stored as
    ``solutions/.progress.html`` and re-derived into ``solutions/problems.json``
    in the same shape the shell's ``summary`` command writes.
    """
    try:
        text = content.decode('utf-8')
    except UnicodeDecodeError as exc:
        return False, f'progress page is not valid UTF-8: {exc}'
    problems = parse_progress(text)
    if not problems:
        return False, ('no problems parsed — paste the full Page Source of '
                       'https://projecteuler.net/progress')
    (repo_root / 'solutions' / '.progress.html').write_text(text, encoding='utf-8')
    (repo_root / 'solutions' / 'problems.json').write_text(
        json.dumps(problems, indent=2), encoding='utf-8')
    return True, f'saved progress — {len(problems)} problems, ' \
                 f'{sum(1 for p in problems.values() if p["solved"])} solved'


# ── about (the footer pages, 5e) ────────────────────────────────────────────────────

#: ``/about/{name}`` → (repo-relative source file, page title, render as markdown?).
#: These are the paths behind the ``about`` object in ``authorizations.json`` —
#: keep the two lists in step so the DD-12 ACL derivation covers exactly them.
ABOUT_PAGES: dict[str, tuple[str, str, bool]] = {
    'readme': ('README.md', 'README', True),
    'license': ('LICENSE', 'MIT license', False),
    'acknowledgements': ('solver/web/content/vendor/README.md', 'Acknowledgements', True),
}


def read_about(repo_root: Path, name: str) -> tuple[str, str, bool] | None:
    """One footer page: (title, raw text, is_markdown), or None (unknown/missing)."""
    entry = ABOUT_PAGES.get(name)
    if entry is None:
        return None
    path, title, is_markdown = entry
    try:
        return title, (repo_root / path).read_text(encoding='utf-8'), is_markdown
    except OSError:
        return None


# ── markdown (docs + topics) ────────────────────────────────────────────────────────

def _doc_slug(text: str) -> str:
    """GitHub-style heading slug — matches `update_doc.py`'s catalogue anchors, so a
    guide's `commands-index.md#command-…` links resolve to the rendered headings."""
    return re.sub(r'[^a-z0-9 -]+', '', text.lower()).strip(' ').replace(' ', '-').strip('-')


def render_markdown(text: str, route_base: str = '/docs/', *, repo_base: str = '') -> str:
    """Render Markdown to HTML: slugged heading ids + links rewired for the shell.

    Each heading gets the same slug `update_doc.py` assumes, so in-page and
    cross-doc `#anchor` links land. Then the link rewrites:

    - a relative ``foo.md`` (or ``docs/foo.md``) link → the *route_base* route;
    - a repo-relative ``../<path>`` link (docs/topics sit one level under the
      repo root, so ``../`` reaches it) → the ``/docs/file/<path>`` view route,
      so a link like ``../solver/templates/authorizations.json`` — which
      resolves natively on GitHub — also resolves in the app viewer;
    - with *repo_base* set (the README, which sits **at** the repo root and so
      links its neighbours with no ``../`` to give them away): every remaining
      relative link and image → the ``/docs/file/`` viewer when it names a
      declared-readable tree, and *repo_base* (GitHub) otherwise. ``LICENSE``,
      ``Makefile``, ``pyproject.toml`` are outside the content ACLs — the viewer
      would 404 on them, so they leave for the source of truth instead;
    - every **internal, absolute** ``/…`` link gets ``hx-*`` attributes so it
      swaps the content pane in place (the shell + terminal persist) instead of
      a full reload. External (``http…``) and ``#anchor`` links are untouched,
      so they navigate/scroll normally.
    """
    tokens = _MD.parse(text)
    for i, token in enumerate(tokens):
        if token.type == 'heading_open':
            token.attrSet('id', _doc_slug(tokens[i + 1].content))
    rendered: str = _MD.renderer.render(tokens, _MD.options, {})
    rendered = re.sub(r'href="(?:docs/)?([\w-]+)\.md(#[^"]*)?"',
                      rf'href="{route_base}\1\2"', rendered)
    rendered = re.sub(r'href="\.\./([^"#]+)"', r'href="/docs/file/\1"', rendered)
    if repo_base:
        rendered = re.sub(r'(<(?:a|img)\b[^>]*?\b(?:href|src)=")(?!\w+:|/|#)([^"]+)"',
                          lambda m: f'{m.group(1)}{_repo_link(m.group(2), repo_base)}"',
                          rendered)
    rendered = re.sub(
        r'<a href="(/[^"]*)"',
        r'<a href="\1" hx-get="\1" hx-target="#content" hx-swap="innerHTML" hx-push-url="true"',
        rendered)
    return rendered


def _repo_link(path: str, repo_base: str) -> str:
    """One README link: the file viewer for a readable tree, else *repo_base* (GitHub).

    The bare ``docs/`` link is the exception — the guides have an index route of
    their own, and the file viewer serves files, not directories.
    """
    if path.rstrip('/') == 'docs':
        return '/docs/'
    root = path.split('/', 1)[0]
    return f'/docs/file/{path}' if root in _README_VIEWABLE else f'{repo_base}{path}'


def _page_title(text: str, fallback: str) -> str:
    """The page's leading `# ` heading, or *fallback*."""
    for line in text.splitlines():
        if line.startswith('# '):
            return line[2:].strip()
    return fallback


def _filename_heading(stem: str) -> str:
    """A readable title from a filename stem: `_`/`-` → space, title-cased
    (e.g. ``convention_c_translation`` → ``Convention C Translation``)."""
    return stem.replace('_', ' ').replace('-', ' ').title()


def _list_pages(tree: Path) -> list[DocEntry]:
    """Index the `*.md` pages of a content tree, sorted by filename (site-design §7)."""
    if not tree.is_dir():
        return []
    entries = []
    for path in sorted(tree.glob('*.md')):
        try:
            text = path.read_text(encoding='utf-8')
        except OSError:
            continue
        entries.append(DocEntry(name=path.stem, heading=_filename_heading(path.stem),
                                title=_page_title(text, path.stem)))
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

#: The project's front page, served as the `readme` doc — it is the one page that
#: says what all the others are *for*, so it belongs in the index the guides sit in
#: (it lives at the repo root, not under `docs/`, hence the special case).
_README_MD = 'README.md'
#: Repo trees the README's relative links may resolve to in the file viewer: the
#: declared-readable ones (DD-12). Anything else leaves for GitHub (`_repo_link`).
_README_VIEWABLE = frozenset({'docs', 'about', 'solutions'})
#: Where a README link the viewer cannot serve goes instead — the source of truth.
README_REPO_BASE = 'https://github.com/vikasmunshi/euler/blob/master/'

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
    """The docs index: the README, then every `docs/*.md` guide plus the composed
    `ai` reference, sorted by filename (site-design §7).

    The README leads rather than taking its place in the sort: it is the page that
    introduces the rest, and a reader who wants the overview should not have to
    know it files under *r*."""
    entries = _list_pages(repo_root / 'docs')
    entries.append(DocEntry(name='ai', heading='AI', title='AI reference'))
    readme = _readme_entry(repo_root)
    return ([readme] if readme else []) + sorted(entries, key=lambda e: e.name)


def _readme_entry(repo_root: Path) -> DocEntry | None:
    """The index row for the README, or None when it is unreadable (never a 500)."""
    try:
        text = (repo_root / _README_MD).read_text(encoding='utf-8')
    except OSError:
        return None
    # Its lead heading is an `##` (the `#` is the repo name on GitHub), so take the
    # first heading of any level rather than _page_title's `# `.
    match = re.search(r'^#{1,3}\s+(.+)$', text, re.MULTILINE)
    return DocEntry(name='readme', heading='README',
                    title=match.group(1).strip() if match else 'The project')


def read_doc(repo_root: Path, name: str) -> str | None:
    """The raw Markdown of `/docs/{name}`: the README, a `docs/` guide, or the
    composed `ai` page."""
    if name in ('ai', 'ai.md'):
        return _compose_ai_doc(repo_root)
    if name in ('readme', 'readme.md'):
        try:
            return (repo_root / _README_MD).read_text(encoding='utf-8')
        except OSError:
            return None
    return _read_page(repo_root / 'docs', name)


# ── topics ──────────────────────────────────────────────────────────────────────────

def list_topics(repo_root: Path) -> list[DocEntry]:
    """The topics index: every `topics/*.md` writeup."""
    return _list_pages(repo_root / 'topics')


def read_topic(repo_root: Path, name: str) -> str | None:
    """The raw Markdown of `/topics/{name}`."""
    return _read_page(repo_root / 'topics', name)

#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Config-free readers for the content trees the service renders.

Every function takes the repo working tree (`SiteConfig.repo_root`) explicitly
and imports nothing from :mod:`solver.config` (which resolves the shell's
identity + per-user state — paths the service uid cannot use). The service reads
exactly the declared content trees — `solutions/` · `docs/` · `topics/` ·
`solver/web/content/` — plus, best-effort, the AI reference sources under
`solver/` for the composed `ai` doc, which degrade to a note when the uid may
not read them.
"""
from __future__ import annotations

__all__ = ['ProblemInfo', 'Century', 'DocEntry', 'TopicGroup', 'SectionState',
           'TEXT_SUFFIXES', 'ABOUT_PAGES', 'SHELL_DOCS', 'CATALOGUE_DOC',
           'solution_dir', 'load_problems', 'centuries', 'problem_files', 'section_state',
           'resolve_file', 'resolve_repo_file', 'load_json', 'render_markdown', 'collapse_problems',
           'rewrite_statement_links', 'recolour_statement', 'plate_statement_images',
           'prepare_statement', 'STATEMENT_COLOURS', 'git_status', 'topic_status',
           'list_docs', 'read_doc', 'shell_docs', 'command_catalogue', 'list_topics', 'list_topic_groups',
           'read_topic', 'drop_article',
           'problem_tag_view',
           'read_about', 'readme_html',
           'parse_progress', 'save_progress']

import json
import mimetypes
import re
import subprocess
from functools import cache
from html import escape
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
    """One row of `problems.json`: the scraped progress-page metadata."""

    number: int
    title: str
    level: int | None
    pct: int | None
    solved: bool
    date: str

    @property
    def heat(self) -> int:
        """Difficulty bucket 1–5 (by `pct`) shading a solved cell in the grid."""
        if not self.pct:
            return 1
        return 1 + min((self.pct - 1) // 20, 4)


class Century(NamedTuple):
    """One 10×10 grid: problems `start` … `start+99` (missing numbers → None)."""

    start: int
    cells: list[ProblemInfo | None]
    solved: int

    @property
    def total(self) -> int:
        """Problems this century actually has — 100, except the last, which stops at the
        highest number projecteuler.net has published. The tile heading the grid reads
        `n of total solved`, so it must count cells, not assume a hundred."""
        return sum(1 for cell in self.cells if cell is not None)


class DocEntry(NamedTuple):
    """A docs/topics index row (web-server-guide § The site): the URL *name*, the *heading*
    derived from the filename (title-cased, separators → spaces — the card's
    first line), and the *title* from the page's leading `#` heading (second
    line). Index lists are sorted by *name* (the filename).

    *status* is carried by topic articles only (`draft` / `final`, from the article
    index); the docs tree leaves it empty. *solved* / *problems* likewise come from the
    article index — how many of the problems behind a topic we have solved — and are
    `None` for any entry read from a bare tree walk, where the counts are unknown
    rather than zero."""

    name: str
    heading: str
    title: str
    status: str = ''
    solved: int | None = None
    problems: int | None = None


class TopicGroup(NamedTuple):
    """One folder of the topics tree: the folder segment, its display *heading*,
    and the pages inside it (each :class:`DocEntry` keeping its full URL *name*).
    Pages sitting directly under `topics/` collect into the group named `''`."""

    name: str
    heading: str
    entries: list[DocEntry]


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
    """The parsed `solutions/problems.json`, cached until the file's mtime moves."""
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
    """The problem's viewable files (mimetype-guessable, as `ls` lists them),
    as POSIX paths relative to the solution directory. **Zero-size files are
    hidden** (web-server-guide § The site) — an empty stub says nothing worth a link."""
    if not sdir.is_dir():
        return []
    return sorted(
        p.relative_to(sdir).as_posix() for p in sdir.rglob('*')
        if p.is_file() and p.stat().st_size > 0
        and mimetypes.guess_type(p.name)[0] is not None
    )


def git_status(repo_root: Path, sdir: Path) -> dict[str, tuple[str, str]]:
    """Best-effort git status for *sdir*: relative name → (css class, hover title).

    Read-only, and the *only* git the web tier runs (no commits, no
    checkouts, no key). It works from the deployed per-profile uids because
    `.git` is world-readable and the query carries its own
    `safe.directory` exception: git otherwise **refuses a repository owned by
    another uid** ("detected dubious ownership") — that ownership check, not the
    file permissions, is what would silence the status colours on a deployed
    instance. `-c` is *protected* configuration scope (like system/global), so
    the exception is honoured; it is scoped to this one invocation rather than
    written into the host's git config, so no other process or uid gains
    anything.

    Any failure still degrades to `{}` (files render plain) — a missing git
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

    *roots* are the **declared-readable** content paths (the `docs` / `about`
    trees — dirs or single files); the returned file must sit under one of them, so
    the `/docs/file/` view can only ever serve what the service declares readable.
    Rejects traversal + symlink escape.
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

    The config-free port of `solver.utils.summary._parse_progress_html`,
    operating on the submitted text (so a bad edit is rejected *before* anything
    lands on disk). Returns `{number: {title, level, pct, solved, date}}` —
    `level`/`pct` are ints or `''` when unknown, matching the shell's
    writer so the two producers of `problems.json` stay interchangeable.
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
    `solutions/.progress.html` and re-derived into `solutions/problems.json`
    in the same shape the shell's `summary` command writes.
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

#: `/about/{name}` → (repo-relative source file, page title, render as markdown?).
#: These are the files behind the footer pages — keep them in step with the service's
#: declared-readable roots (`install_content`), which is what admits them.
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


def rewrite_statement_links(html: str, number: int) -> str:
    """Root a cached statement's relative resource links at the problem's canonical path.

    projecteuler.net markup links its images and data files relatively
    (`src="resources/0096_1.png"`). On a full page load those resolve under the
    page's own `/solutions/NNNN/` URL and work — but the pane is normally reached by
    an htmx swap, where the relative URL is resolved against the *previous* page's URL
    (still `/solutions/` at swap time), so `resources/…` becomes
    `/solutions/resources/…` and 404s — the images silently break. Rewriting them to
    the absolute `/solutions/NNNN/…` path (the same route :func:`resolve_file` serves)
    makes them resolve identically however the page was reached. Scheme (`http:`),
    already-absolute (`/…`) and anchor (`#`) URLs are left untouched.
    """
    base = f'/solutions/{number:04d}/'
    return re.sub(r'(<(?:a|img)\b[^>]*?\b(?:href|src)=")(?!\w+:|/|#)([^"]+)"',
                  lambda m: f'{m.group(1)}{base}{m.group(2)}"', html)


#: projecteuler.net's emphasis colours, remapped for a dark ground. Their markup is
#: written for a light page, where a saturated primary reads as emphasis; on ours the
#: same value is a dark mark on a dark field — `#3333ff` on `#0f1115` is the case that
#: started this. Each entry is the same hue, lifted in luminance and desaturated enough
#: to sit on `--bg` without glowing: the author's *intent* (this bit is marked) survives,
#: which is the thing worth keeping. Their exact byte was never the point.
#:
#: Keyed by the token as it appears in the source, and matched case-insensitively, so one
#: table serves all three ways a statement asks for a colour (below).
STATEMENT_COLOURS: dict[str, str] = {
    'red': '#ff8781', 'blue': '#7cc0ff', 'green': '#7ee787', 'orange': '#ffb26b',
    '#ff0000': '#ff8781', '#3333ff': '#7cc0ff', '#00ff00': '#7ee787',
}

#: `\color{red}` / `\color{#FF0000}` inside the LaTeX MathJax renders. This is where the
#: reported case lived: the colour is not HTML at all, so no stylesheet can reach it —
#: MathJax has already turned it into a fill by the time CSS applies. Rewriting the source
#: before it reaches the browser is the only hook, and it is the same hook for both forms.
#:
#: A form that already names a model (`\color[rgb]{…}`) does not match, and is left alone:
#: whoever wrote that said exactly what they meant.
_TEX_COLOUR_RE = re.compile(r'\\color\s*\{\s*([A-Za-z]+|#[0-9A-Fa-f]{3,6})\s*\}')


def _tex_colour(hex_colour: str) -> str:
    r"""A `\color` directive for *hex_colour* — as `[RGB]{r,g,b}`, never as a `#` literal.

    **`#` must never reach the TeX.** It is the macro-parameter character, and whether it
    is fatal depends on a race: `\color` arrives from an autoloaded extension, so on the
    first statement to use it MathJax parses the argument as ordinary math while the
    extension is still in flight — and there `#` is "You can't use 'macro parameter
    character #' in math mode", which is a rendered error, not a retry.

    That is exactly what a `#7cc0ff` rewrite did to p0238, and it hid well: reaching the
    page by htmx swap hit the window and failed, while a plain refresh had the extension
    cached and rendered perfectly. `\color{blue}` never showed it because `{blue}` is
    valid math — four italic letters — so the same race was invisible for every colour
    projecteuler.net actually writes.

    `[RGB]{r,g,b}` is the LaTeX-standard model form (the vendored `color.js` implements
    `rgb`, `RGB`, `gray` and `named` — there is no `HTML` model), and it carries no
    character that math mode objects to. Tested both ways: with the extension loaded it
    colours, and with it missing entirely it still raises no error.
    """
    digits = hex_colour.lstrip('#')
    if len(digits) == 3:
        digits = ''.join(c * 2 for c in digits)
    red, green, blue = (int(digits[i:i + 2], 16) for i in (0, 2, 4))
    return f'\\color[RGB]{{{red},{green},{blue}}}'


#: An inline `style="color:#FF0000"`. CSS could only beat this with `!important`, and a
#: sheet that has to shout at its own content is a sheet that will lose the next round.
_CSS_COLOUR_RE = re.compile(r'(color\s*:\s*)(#[0-9A-Fa-f]{3,6}|[A-Za-z]+)')


def recolour_statement(html: str) -> str:
    """Remap a cached statement's emphasis colours for the dark ground.

    Three ways projecteuler.net colours a statement, and this reaches all three: the LaTeX
    `\\color{…}` MathJax renders, an inline `style="color:…"`, and — via
    :data:`STATEMENT_COLOURS` and the stylesheet's `.statement .red` rules — their
    `class="red"` spans. Only the tokens in the table are touched; anything else is left
    exactly as written, so an unrecognised colour renders as it always did rather than as
    whatever this guessed.
    """
    def tex(match: re.Match[str]) -> str:
        mapped = STATEMENT_COLOURS.get(match.group(1).lower())
        # The whole directive is replaced, not just the value: the replacement names a
        # colour *model* (`[RGB]`), which is what keeps `#` out of the math (:func:`_tex_colour`).
        return _tex_colour(mapped) if mapped else match.group(0)

    def css(match: re.Match[str]) -> str:
        mapped = STATEMENT_COLOURS.get(match.group(2).lower())
        return f'{match.group(1)}{mapped}' if mapped else match.group(0)

    return _CSS_COLOUR_RE.sub(css, _TEX_COLOUR_RE.sub(tex, html))


#: Above this share of see-through pixels an image has no background of its own, so it
#: takes the page's — which is the whole problem. Below it the image brings its own ground
#: and is readable on any page, so it is left alone.
_TRANSPARENT_AT: float = 0.15
#: Mean luminance (0–255) of the visible pixels, above which the ink is light. Light ink is
#: what a dark page wants, so those are the images that must NOT be plated.
_LIGHT_INK_AT: float = 140.0
#: Sampling stride. These are diagrams a few hundred pixels square, so every fourth pixel
#: fixes the mean at a quarter of the work. Measured against a full scan of all 254 cached
#: images it changes exactly one verdict — an image whose ink means 139.8 against a
#: threshold of 140. That one is not the stride being lossy, it is a genuinely mid-grey
#: diagram that reads on either ground; nothing near the thresholds moves for any other.
_INK_STRIDE: int = 4


@cache
def _image_ink(path: Path, stamp: tuple[int, int]) -> str:
    """Classify *path*'s ink: `'dark'`, `'light'`, or `''` when it needs no plate.

    projecteuler.net's diagrams are transparent PNGs and GIFs, so the page shows through
    them and the ink has to contrast with *our* ground. It does not always: 44 of the
    cached images are dark line art on nothing, which on `--bg` is a black diagram on a
    near-black field — invisible, on problems as ordinary as 15 and 86. Another 28 are the
    opposite, light ink that a dark page suits exactly. `class="dark_img"`, which
    projecteuler puts on the ones it serves to dark themes, does not tell them apart in our
    cache (37 of the dark-ink images carry it), so the pixels are the only honest source.

    `''` for an opaque image (it carries its own background, so the page's ground never
    reaches it), for a format Pillow cannot open, and for every image if Pillow is absent —
    each of which means "no plate", which is exactly today's rendering. A statement must
    render whatever this can or cannot decide about a picture in it.

    *stamp* is the file's `(mtime_ns, size)`. It is not read — it is in the key so a
    replaced image is re-measured rather than answered from the cache.
    """
    del stamp
    try:
        from PIL import Image
    except ImportError:                                     # pragma: no cover - env-dependent
        return ''
    try:
        with Image.open(path) as handle:
            # `tobytes()` on the converted image, not `getdata()`: the latter is deprecated
            # and goes away in Pillow 14. Four bytes per pixel, RGBA in order, which is a
            # flat buffer to stride through rather than a list of tuples to allocate.
            raw = handle.convert('RGBA').tobytes()
    except (OSError, ValueError):
        return ''
    step = 4 * _INK_STRIDE
    total = visible = 0
    luminance = 0.0
    for i in range(0, len(raw) - 3, step):
        total += 1
        if raw[i + 3] > 128:
            visible += 1
            luminance += 0.2126 * raw[i] + 0.7152 * raw[i + 1] + 0.0722 * raw[i + 2]
    if not total or not visible or (total - visible) / total < _TRANSPARENT_AT:
        return ''
    return 'light' if luminance / visible > _LIGHT_INK_AT else 'dark'


def plate_statement_images(html: str, number: int, sdir: Path) -> str:
    """Mark each statement image with the ground it needs: `ink-dark` gets a plate.

    Adds a class the stylesheet acts on, rather than a style: what a plated image should
    look like — how much padding, how round, how white — is the sheet's business, and this
    only answers the question the sheet cannot, which is what is *in* the picture.

    Runs after :func:`rewrite_statement_links`, so `src` is the rooted `/solutions/NNNN/…`
    path — hence *number*, which rebuilds the same prefix that pass added and strips it to
    get back to the path on disk. (Taking the directory's own name instead does not work:
    *sdir* is `…/p0015` while the route is `/solutions/0015/`.) An image that does not
    resolve under *sdir* — an off-site `src`, a resource that never downloaded — is left
    alone, the same "no plate" as an undecidable one.
    """
    base = f'/solutions/{number:04d}/'

    def mark(match: re.Match[str]) -> str:
        tag, src = match.group(0), match.group(1)
        if not src.startswith(base):
            return tag
        rel = src[len(base):]
        target = sdir / rel
        if '..' in rel or not target.is_file():
            return tag
        try:
            stat = target.stat()
        except OSError:
            return tag
        ink = _image_ink(target, (stat.st_mtime_ns, stat.st_size))
        if not ink:
            return tag
        klass = f'ink-{ink}'
        if 'class="' in tag:
            return tag.replace('class="', f'class="{klass} ', 1)
        return tag.replace('<img', f'<img class="{klass}"', 1)

    return re.sub(r'<img\b[^>]*?\bsrc="([^"]+)"[^>]*>', mark, html)


def prepare_statement(html: str, number: int, sdir: Path) -> str:
    """A cached statement, ready for a dark page: links rooted, colours and ink remapped.

    The three passes in the order they depend on each other — links first, because the
    plate step reads the rooted `src` to find the file on disk. Composed here so the one
    caller states what it wants ("prepare this statement") rather than the recipe.
    """
    return plate_statement_images(recolour_statement(rewrite_statement_links(html, number)),
                                  number, sdir)


# ── markdown (docs + topics) ────────────────────────────────────────────────────────

def _doc_slug(text: str) -> str:
    """GitHub-style heading slug — matches `update_doc.py`'s catalogue anchors, so a
    guide's `commands-index.md#command-…` links resolve to the rendered headings."""
    return re.sub(r'[^a-z0-9 -]+', '', text.lower()).strip(' ').replace(' ', '-').strip('-')


#: What the masker walks, in precedence order. The first three alternatives are
#: *shields* — matched only so that math cannot be found inside them, and handed
#: back to the renderer untouched:
#:
#: - `fence` / `code`: fenced blocks and inline code spans. MathJax's own defaults
#:   skip `<pre>`/`<code>` (see `site.js`), so a `$…$` in a snippet is not math and
#:   must keep its backslashes *literal* — exactly what CommonMark already does there;
#: - `esc`: `\$`, the documented escape for a literal dollar
#:   (`convention_documentation.md`). Consuming it here stops it opening a span,
#:   and leaves CommonMark to unescape it to a plain `$` as the convention promises.
#:
#: Then the two math forms, MathJax's configured delimiters (`site.js`: inline
#: `$…$`, display `$$…$$`), display first so `$$` wins the tie. Inline math may
#: cross a line — the corpus wraps it — but never a blank line: an unpaired `$` in
#: prose then swallows a couple of lines at worst, not the rest of the document.
_MASK_RE = re.compile(
    r'(?P<fence>^ {0,3}(?P<f>```+|~~~+)[\s\S]*?(?:^ {0,3}(?P=f)[^\n]*$|\Z))'
    r'|(?P<code>(?<!`)(?P<t>`+)(?!`)[\s\S]*?(?<!`)(?P=t)(?!`))'
    r'|(?P<esc>\\\$)'
    r'|(?P<display>\$\$(?:[^$]|\$(?!\$))+?\$\$)'
    r'|(?P<inline>\$(?!\$)(?:[^$\n]|\n(?![ \t]*\n))+?\$)',
    re.M)

#: The stand-in a math span is parked under. Private-use codepoints: no Markdown
#: meaning, nothing the inline parser will touch, and nothing an article can contain.
_MASK_FMT = '\ue000{}\ue000'

#: The same slot, read back: the index in it names which span belongs there.
_MASK_SLOT = re.compile('\ue000([0-9]+)\ue000')


def _mask_math(text: str) -> tuple[str, list[str]]:
    """Lift every math span out of *text*, leaving a placeholder in its place.

    CommonMark backslash-escapes run over the whole document, and TeX is full of
    escaped ASCII punctuation: `\\,` `\\;` `\\{` `\\#` `\\%` `\\\\` all mean something
    to MathJax and all are *escapable* characters, so the renderer ate the backslash
    and MathJax got the bare character. Depending on which one, that is a hard error
    (`\\#` → "You can't use 'macro parameter character #' in math mode"), a silently
    wrong render (`\\{…\\}` losing its braces, `\\,` becoming a comma between factors),
    or a swallowed line (`\\%` opening a TeX comment).

    Masking is the fix that scales past the corpus: the spans never reach the inline
    parser, so no article has to be written around the renderer's escape table.
    """
    spans: list[str] = []

    def take(m: re.Match[str]) -> str:
        math = m.group('display') or m.group('inline')
        if math is None:
            return m.group(0)             # a shield: code, a fence, or an escaped dollar
        spans.append(math)
        return _MASK_FMT.format(len(spans) - 1)

    return _MASK_RE.sub(take, text), spans


def _unmask_math(text: str, spans: list[str], *, raw: bool = False) -> str:
    """Put the math spans back where their placeholders sit.

    Into HTML they go back **escaped**, as the renderer would have escaped them:
    that costs nothing, because MathJax reads *text* and so gets the `<` the author
    wrote back out of `&lt;`, while the browser never sees markup an article did not
    intend to emit. *raw* is for the heading slugs, which are computed from source
    text and would otherwise anchor on `&amp;`.
    """
    return _MASK_SLOT.sub(lambda m: spans[int(m.group(1))] if raw else escape(spans[int(m.group(1))], quote=False),
                          text)


#: A paragraph that is **nothing but** a bold sentence — the pull-quote a writer means by
#: giving a line a paragraph of its own — gets `class="pull"` so a stylesheet can tell it
#: from the bold that merely *opens* or *ends* a paragraph. CSS cannot make that
#: distinction itself: `p > strong:only-child` counts element siblings, and the text after
#: `**…**` is a text node, so every lead-in bold matches it too. The markup is where the
#: difference is real, so the mark is made here, once, for every tree that renders.
_PULL_RE = re.compile(r'<p>(<strong>(?:(?!</strong>).)*</strong>)</p>', re.DOTALL)


def render_markdown(text: str, route_base: str = '/docs/', *, repo_base: str = '') -> str:
    """Render Markdown to HTML: slugged heading ids + links rewired for the shell.

    Math spans (`$…$`, `$$…$$`) ride around the parser untouched — see
    :func:`_mask_math` for why they have to.

    Each heading gets the same slug `update_doc.py` assumes, so in-page and
    cross-doc `#anchor` links land. Then the link rewrites:

    - a relative `foo.md` (or `docs/foo.md`) link → the *route_base* route;
    - a repo-relative `../<path>` link (docs/topics sit one level under the
      repo root, so `../` reaches it) → the `/docs/file/<path>` view route when
      that route can serve it (:data:`VIEWABLE_ROOTS`), and **GitHub otherwise**.
      This used to be unconditional, on the assumption that a link resolving
      natively on GitHub also resolved in the viewer — but `/docs/file/` serves
      only the declared trees and deliberately not the wider `solver/` source, so
      every `../solver/…` link in a guide rendered as a live link to a 404. The
      repository is public, so the honest destination for those is GitHub;
    - with *repo_base* set (the README, which sits **at** the repo root and so
      links its neighbours with no `../` to give them away): every remaining
      relative link and image → the `/docs/file/` viewer when it names a
      declared-readable tree, and *repo_base* (GitHub) otherwise. `LICENSE`,
      `Makefile`, `pyproject.toml` are outside the content ACLs — the viewer
      would 404 on them, so they leave for the source of truth instead;
    - every **internal, absolute** `/…` link gets `hx-*` attributes so it
      swaps the content pane in place (the shell + terminal persist) instead of
      a full reload. External (`http…`) and `#anchor` links are untouched,
      so they navigate/scroll normally.
    """
    masked, spans = _mask_math(text)
    tokens = _MD.parse(masked)
    for i, token in enumerate(tokens):
        if token.type == 'heading_open':
            # The slug is the *source* heading's, math and all, so `#anchor` links
            # written against the article (and `update_doc.py`'s) still land.
            token.attrSet('id', _doc_slug(_unmask_math(tokens[i + 1].content, spans, raw=True)))
    rendered: str = _MD.renderer.render(tokens, _MD.options, {})
    rendered = _PULL_RE.sub(r'<p class="pull">\1</p>', rendered)
    rendered = re.sub(r'href="(?:docs/)?([\w-]+)\.md(#[^"]*)?"',
                      rf'href="{route_base}\1\2"', rendered)
    rendered = re.sub(r'href="\.\./([^"#]+)"',
                      lambda m: f'href="{_repo_link(m.group(1), repo_base or README_REPO_BASE)}"',
                      rendered)
    if repo_base:
        rendered = re.sub(r'(<(?:a|img)\b[^>]*?\b(?:href|src)=")(?!\w+:|/|#)([^"]+)"',
                          lambda m: f'{m.group(1)}{_repo_link(m.group(2), repo_base)}"',
                          rendered)
    rendered = re.sub(
        r'<a href="(/[^"]*)"',
        r'<a href="\1" hx-get="\1" hx-target="#content" hx-swap="innerHTML" hx-push-url="true"',
        rendered)
    return _unmask_math(rendered, spans)   # last: no link rewrite may reach inside a formula


#: The rendered form of `update-tags`' problems block: its opening HTML-comment marker,
#: the `## Problems` heading (its `id` anchor kept), the list, then the closing marker.
#: Matched on the rendered HTML — the comments survive `render_markdown` — so the source
#: article is never rewritten; `update-tags` still round-trips its own markers.
_RENDERED_PROBLEMS_RE = re.compile(
    r'<!--\s*problems \(generated by update-tags\)\s*-->\s*'
    r'<h2 id="problems">(?P<title>.*?)</h2>\s*'
    r'(?P<list>.*?)\s*'
    r'<!--\s*/problems\s*-->',
    re.DOTALL)


def collapse_problems(html: str, problems: dict[int, ProblemInfo] | None = None) -> str:
    """Fold a topic's generated Problems list into a collapsed `<details>` (click to expand).

    The block `update-tags` writes can run to dozens of entries and pushes the article's
    prose off-screen, so on the topic page it renders collapsed: a `<summary>` carrying the
    `## Problems` heading — its `id="problems"` anchor preserved so `#problems` links still
    land — and the entry count, with the list revealed on click. Purely presentational: the
    source article keeps the plain heading-and-list that renders on GitHub. An article
    without the block is returned unchanged.

    With *problems* given (the parsed `problems.json`), the count reads `solved / total`
    — the numbers taken from *this clone's* progress against the `/solutions/NNNN/` links
    the list carries, so it stays live rather than frozen at the last `update-tags`.
    Without it (the default) the bare total is shown, as before.
    """
    def _wrap(match: re.Match[str]) -> str:
        listing = match.group('list')
        if problems is not None:
            # Anchor on href= so each entry counts once — render_markdown boosts the
            # link, so the number also appears in an hx-get on the same anchor.
            numbers = [int(n) for n in re.findall(r'href="/solutions/(\d+)/', listing)]
            solved = sum(1 for n in numbers
                         if (info := problems.get(n)) is not None and info.solved)
            label = f'{solved} / {len(numbers)}'
        else:
            label = str(listing.count('<li>'))
        return ('<details class="fold topic-problems">'
                '<summary class="fold-summary">'
                f'<h2 id="problems" class="fold-title">{match.group("title")}'
                f'<span class="problems-count">{label}</span></h2></summary>'
                f'{listing}'
                '</details>')
    return _RENDERED_PROBLEMS_RE.sub(_wrap, html)


def _repo_link(path: str, repo_base: str) -> str:
    """One repo-relative link: the file viewer when it can serve the path, else GitHub.

    The bare `docs/` link is the exception — the guides have an index route of
    their own, and the file viewer serves files, not directories.
    """
    if path.rstrip('/') == 'docs':
        return '/docs/'
    return f'/docs/file/{path}' if _viewable(path) else f'{repo_base}{path}'


def _page_title(text: str, fallback: str) -> str:
    """The page's leading `# ` heading, or *fallback*."""
    for line in text.splitlines():
        if line.startswith('# '):
            return line[2:].strip()
    return fallback


def _filename_heading(stem: str) -> str:
    """A readable title from a filename stem: `_`/`-` → space, title-cased
    (e.g. `convention_c_translation` → `Convention C Translation`)."""
    return stem.replace('_', ' ').replace('-', ' ').title()


def _list_pages(tree: Path) -> list[DocEntry]:
    """Index the `*.md` pages of a content tree, sorted by filename (web-server-guide § The site)."""
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
#: The repo-relative prefixes `/docs/file/` may serve — **the** list, read by the service
#: (`solver.web.site.app.build_app`) to scope the route and by :func:`_viewable` to decide
#: where a link should point. One list, because the two answers must agree: a link rewritten
#: to a route that then refuses it is a 404 nobody sees until they click it, which is exactly
#: what happened to `../solver/…` links for as long as the rewrite was unconditional.
#:
#: `LICENSE` is deliberately absent though the route used to allow it: it has no suffix, so
#: :data:`TEXT_SUFFIXES` misses it and the viewer would hand the browser a download rather
#: than a page. The README always linked it to GitHub for that reason, and now the route
#: agrees rather than offering a capability nobody could use.
VIEWABLE_ROOTS: tuple[str, ...] = ('docs/', 'topics/', 'solver/templates/', 'solutions/',
                                   'README.md', 'solver/web/content/vendor/README.md')
#: Where a link the viewer cannot serve goes instead — the source of truth. The repository is
#: public, so every path that is not viewable here is readable there.
README_REPO_BASE = 'https://github.com/vikasmunshi/euler/blob/master/'


def _viewable(path: str) -> bool:
    """Whether `/docs/file/<path>` can actually serve this — i.e. whether to link it there."""
    return any(path == root or path.startswith(root) for root in VIEWABLE_ROOTS)


#: The packaged start-page **summary** — a tracked, generated file (the
#: `update-docs` command rebuilds it from the README's HOME slice), shipped inside
#: the distribution as package data. It is a *summary* of the README, not the whole
#: file; the "read the full README" link on the start page leads to the rest.
#:
#: The start page renders THIS copy in both tiers, while `/docs/readme` and
#: `/about/readme` keep reading the clone's full README. That is not an
#: inconsistency, it is the two contracts: the docs viewer shows *this clone's*
#: docs (a contributor editing them must see their own edit), whereas the start
#: page is chrome — it is served by the auth tier too, which runs from /opt/euler
#: with ProtectHome=true and has no clone to read, and it must say the same thing
#: to everyone whatever branch they are on.
_HOME_SUMMARY = Path(__file__).resolve().parent.parent / 'content' / 'home-summary.md'


@cache
def readme_html() -> str:
    """The packaged start-page summary rendered to HTML, or `''` if missing.

    Cached for the process's life: the file is package data, so it cannot change
    without a reinstall, and a reinstall restarts the services. The start page is
    the most-hit route in both tiers and this is the only markdown parse on it —
    doing it once per process rather than once per request.

    Empty is a deliberate degradation, not an error: a tree where the summary was
    never generated (a developer who has never run `update-docs`) still gets a
    working start page, just without the summary under its cards.
    """
    try:
        text = _HOME_SUMMARY.read_text(encoding='utf-8')
    except OSError:
        return ''
    return render_markdown(text, repo_base=README_REPO_BASE)


#: The AI reference sources composed into the `ai` doc. They live under `solver/`
#: — outside the content ACLs — so each is read best-effort (see `_ai_section`).
#: Every skill under `skills/` is composed in, so a new one appears here by existing
#: rather than by being added to a list that the last one was forgotten from.
_AI_SKILLS_DIR = 'solver/ai/claude/skills'
_AI_PROMPTS_DIR = 'solver/templates'

_AI_INTRO = """\
# AI reference

The framework's AI paths, collated into one reference. The shell's `claude-solve`
command runs Claude Code **headless** against a single problem's solution files
(the **claude-euler-solver** skill), and `claude-blog` runs it against one topic
article under `topics/` (the **claude-euler-blogger** skill); both skills are
below. `claude-api` generates solution artifacts — Python and C code,
`notes.html`, `test_cases.json` — through the Claude API from the **prompt
templates** further down. All of them are held to the shared `convention_*`
guides listed in the [docs index](/docs/).
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

    The sources live under `solver/` — outside the declared content trees — so a
    deployed service uid may lack read on them; the page degrades rather than 500s
    (in a dev run as the owner it renders in full).
    """
    if body:
        return f'{heading}\n\n{body}'
    return f'{heading}\n\n*`{path.as_posix()}` is not readable by this service.*'


def _compose_ai_doc(repo_root: Path) -> str:
    """The `ai` doc's Markdown: intro + the skill definition + the prompt templates."""
    sections = [_AI_INTRO]
    skills_dir = repo_root / _AI_SKILLS_DIR
    try:
        skills = sorted(skills_dir.glob('*/SKILL.md'))
    except OSError:
        skills = []
    if not skills:  # unreadable dir, or none installed — say so rather than silently drop them
        sections.append(_ai_section('## The Claude Code skills', Path(_AI_SKILLS_DIR), ''))
    for skill in skills:
        try:
            skill_body = _strip_frontmatter(skill.read_text(encoding='utf-8'))
        except OSError:
            skill_body = ''
        sections.append(_ai_section(f'## The {skill.parent.name} skill',
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
    `ai` reference, sorted by filename (web-server-guide § The site).

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


#: The guides the **terminal** page offers (web-server-guide § The site): the four a
#: reader standing at a prompt actually reaches for — how to invoke the shell, how to
#: solve with it, what it can be told, and the grammar it is told in. The docs index
#: holds a dozen more; this page is not that index, it is the shelf beside the prompt.
#: Order is the reading order, not the filename's — the guide first, the reference last.
SHELL_DOCS: tuple[str, ...] = ('user-guide', 'solver-guide', 'commands-index', 'syntax')


def shell_docs(repo_root: Path) -> list[DocEntry]:
    """The :data:`SHELL_DOCS` guides as index rows, in that order.

    Reads only those four pages rather than indexing the whole tree: the terminal page
    shows a fixed shelf, and `list_docs` would read every guide (one of them very large)
    to title it. A guide missing from this clone is simply absent — a tree that has been
    pruned renders a shorter shelf, never a 404."""
    tree = repo_root / 'docs'
    entries = []
    for name in SHELL_DOCS:
        text = _read_page(tree, name)
        if text is None:
            continue
        entries.append(DocEntry(name=name, heading=_filename_heading(name),
                                title=_page_title(text, name)))
    return entries


#: The one-page command catalogue (`docs/commands-catalogue.md`) — the compact
#: `name · aliases · requires · description` table, generated into that file from the
#: live registry by `update-docs`. The terminal page renders it beside the shell; the
#: user guide shows the same generated block inside its own narrative.
CATALOGUE_DOC = 'commands-catalogue'


def command_catalogue(repo_root: Path) -> tuple[str, int]:
    """The rendered command catalogue and how many commands it lists.

    The count is read off the rendered table rather than the registry: this service does
    not import the shell (the command modules pull in prompt-toolkit and resolve the
    shell's identity), and the page's own table is the honest answer to "how many rows
    are below this rule" whatever the clone's `update-docs` last wrote. `<thead>`
    contributes the one row that is not a command."""
    html = render_markdown(_read_page(repo_root / 'docs', CATALOGUE_DOC) or '')
    return html, max(html.count('<tr>') - 1, 0)


def _docs_count(repo_root: Path) -> int:
    """How many rows :func:`list_docs` would return — counted by `stat`, not by reading.

    The section strip carries this on every one of the five pages, and `list_docs` reads
    each guide's body to title it (`web-server-guide.md` alone is a novel). The count
    only needs to know which files *exist*. Keep the arithmetic in step with `list_docs`:
    the README when it is readable, every `docs/*.md`, and the composed `ai` page."""
    tree = repo_root / 'docs'
    guides = sum(1 for _ in tree.glob('*.md')) if tree.is_dir() else 0
    return guides + 1 + (1 if (repo_root / _README_MD).is_file() else 0)


# ── topics ──────────────────────────────────────────────────────────────────────────

def list_topics(repo_root: Path) -> list[DocEntry]:
    """The topics index: every `topics/**/*.md` writeup, nested folders included.

    A nested page's `name` is its folder-qualified path (`number-theory/primes`)
    and its `heading` shows the folder trail (`Number Theory / Primes`); sorting by
    the full path keeps same-folder pages together in the card grid.
    """
    tree = repo_root / 'topics'
    if not tree.is_dir():
        return []
    entries: list[DocEntry] = []
    for path in sorted(tree.rglob('*.md')):
        try:
            text = path.read_text(encoding='utf-8')
        except OSError:
            continue
        rel = path.relative_to(tree).with_suffix('')
        entries.append(DocEntry(name=rel.as_posix(),
                                heading=' / '.join(_filename_heading(part) for part in rel.parts),
                                title=_page_title(text, path.stem)))
    return entries


def _indexed_topics(repo_root: Path) -> list[DocEntry]:
    """The written pages of the article index (`topics/articles.json`, maintained by
    `update-tags`) — with their status and their solved/problem counts. Its `missing`
    rows are vocabulary rather than pages, so they are dropped: there is nothing to open.
    Empty when the index is absent or unreadable, which sends the caller back to walking
    the tree.

    A row written before the counts existed simply has none: they stay `None` and the
    card falls back to the page's title, rather than claiming "solved 0 of 0"."""
    data = load_json(repo_root / 'topics' / 'articles.json')
    rows = data.get('articles', []) if isinstance(data, dict) else []
    return [DocEntry(name=str(row['path']), heading=str(row['path']),
                     title=str(row.get('title', '')), status=str(row.get('status', '')),
                     solved=_count(row.get('solved')), problems=_count(row.get('problems')))
            for row in rows
            if isinstance(row, dict) and row.get('path') and row.get('status') in ('draft', 'final')]


def _count(value: Any) -> int | None:
    """One index count: a non-negative int, or None when the row does not carry it."""
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None


def list_topic_groups(repo_root: Path, *, drafts: bool = False,
                      by_coverage: bool = False) -> list[TopicGroup]:
    """The topics index, folded by folder.

    The article index is the source when it is there (it alone knows each page's status);
    otherwise the tree is walked as :func:`list_topics` does, statusless.

    `drafts` decides *which* pages: by default only the finished ones, because update-tags
    now creates a skeleton for every tag and a reader offered six hundred TODO stubs cannot
    find the handful worth reading. The maintainer view passes `drafts=True` to see the
    writing queue. A statusless fallback (no index on disk) lists everything either way —
    there is nothing to filter on, and showing nothing would be worse.

    `by_coverage` orders the cards within each folder by *reach* — the problems the topic's
    tags cover, the count the card already shows — widest first, ties broken by path so the
    order is stable. It is the writing queue's order: alphabetical says nothing about what
    is worth writing next, and the number the maintainer is choosing on is the one on the
    card. Entries with no count (a tree read without the index) sort last, keeping their
    path order. The reader's index stays alphabetical, where a page is looked up by name.

    The folder is the section heading, so each card drops the trail and shows only
    its leaf heading. Groups come out in path order, the pages loose at the root of
    `topics/` (if any) first under a generic heading. Every card keeps a *title* — the
    page's own heading, or its leaf slug when it has none — so all cards carry a second
    line and stand the same height in the grid.
    """
    # `or list_topics(...)` only when the index is *absent*. An index that filters to nothing
    # (no page is final yet) must list nothing - falling back there would show every draft,
    # which is precisely what the filter exists to prevent.
    indexed = _indexed_topics(repo_root)
    entries = ([entry for entry in indexed if drafts or entry.status == 'final']
               if indexed else list_topics(repo_root))
    groups: dict[str, list[DocEntry]] = {}
    for entry in entries:
        folder, _, leaf = entry.name.rpartition('/')
        heading = _filename_heading(leaf)
        title = entry.title or leaf
        groups.setdefault(folder, []).append(entry._replace(heading=heading, title=title))
    order = (lambda e: (-(e.problems if e.problems is not None else -1), e.name)) if by_coverage \
        else (lambda e: (0, e.name))
    return [TopicGroup(name=folder, heading=_filename_heading(folder) if folder else 'General',
                       entries=sorted(entries, key=order))
            for folder, entries in sorted(groups.items())]


# ── the section strip ───────────────────────────────────────────────────────────────
#
# The four tiles that head every one of the five index pages (web-server-guide § The
# site). They carry live counts rather than prose: a row that repeats the header's nav
# on five pages has to say something the header cannot, and four sentences repeated five
# times say nothing. Everything here is a *count* — the tile's mono data line.

#: A problem reference in an article's index row, as `update-tags` writes them (`p0244`).
#: A row may also reference things that are not problems; those simply do not match.
_REF_RE = re.compile(r'p?(\d+)$')

#: mtime-keyed cache of the topic coverage read, per articles.json path. The index is
#: ~650 rows and the strip wants it on every navigation, so it is parsed once per write.
_coverage_cache: dict[Path, tuple[float, tuple[int, frozenset[int]]]] = {}


def _topic_coverage(repo_root: Path) -> tuple[int, frozenset[int]]:
    """`(written, reached)` — how many topic pages are finished, and which problems they
    reach between them, from the article index (`topics/articles.json`).

    The union, not the sum: two topics that both cover problem 42 have covered one
    problem, and a strip tile that adds them up would claim coverage the site does not
    have. Drafts are excluded for the same reason `/topics/` excludes them — a skeleton
    page written by `update-tags` covers nothing a reader can read."""
    path = repo_root / 'topics' / 'articles.json'
    try:
        mtime = path.stat().st_mtime
    except OSError:
        return 0, frozenset()
    cached = _coverage_cache.get(path)
    if cached is not None and cached[0] == mtime:
        return cached[1]
    data = load_json(path)
    rows = data.get('articles', []) if isinstance(data, dict) else []
    written, reached = 0, set()
    for row in rows:
        if not isinstance(row, dict) or row.get('status') != 'final':
            continue
        written += 1
        for ref in row.get('refs') or []:
            match = _REF_RE.fullmatch(str(ref))
            if match:
                reached.add(int(match.group(1)))
    state = (written, frozenset(reached))
    _coverage_cache[path] = (mtime, state)
    return state


class SectionState(NamedTuple):
    """The four section tiles' data lines: solutions, docs, topics, terminal.

    The terminal tile's state is not here — it is the live socket, which only the
    browser knows (`[data-term-dot]`, site.js paints it from the iframe's report)."""

    solved: int
    total: int
    docs: int
    topics: int
    covered: int


def section_state(repo_root: Path) -> SectionState:
    """The section strip's counts for this clone (web-server-guide § The site).

    Cheap enough for every navigation: problems.json and the article index are both
    mtime-cached, and the docs count is a directory scan that reads nothing."""
    problems = load_problems(repo_root)
    written, reached = _topic_coverage(repo_root)
    return SectionState(
        solved=sum(1 for p in problems.values() if p.solved),
        total=len(problems),
        docs=_docs_count(repo_root),
        topics=written,
        # Only problems this clone actually publishes: an index that still references a
        # problem dropped from problems.json must not push the count past the total.
        covered=len(reached & problems.keys()),
    )


#: An article's own status comment. Mirrors `solver.core.tags.article_status`, deliberately
#: rather than importing it: that module pulls in the shell framework (prompt-toolkit and the
#: command registry), which has no business inside a web service. Three lines of regex is the
#: cheaper coupling.
_ARTICLE_STATUS_RE = re.compile(r'<!--\s*status:\s*(\w+)\s*-->', re.IGNORECASE)


def topic_status(text: str) -> str:
    """An article's status: `final` only when it says so, else `draft`.

    A page on disk is never `missing` however its comment reads - the file is the fact.
    """
    m = _ARTICLE_STATUS_RE.search(text)
    return 'final' if m and m.group(1).lower() == 'final' else 'draft'


def read_topic(repo_root: Path, name: str) -> str | None:
    """The raw Markdown of `/topics/{name}`, where *name* may be a nested `folder/page` path."""
    return _read_nested_page(repo_root / 'topics', name)


def drop_article(repo_root: Path, name: str) -> None:
    """Best-effort removal of *name*'s row from `topics/articles.json`.

    The article file is the page; the index is the catalogue. Deleting the file alone would
    leave a dangling index row — `_indexed_topics` would keep listing a page that now 404s —
    so the matching `path == name` row is dropped here too. Best-effort by design: an
    absent or malformed index is left untouched, and `update-tags` reconciles it fully on
    its next run.
    """
    path = repo_root / 'topics' / 'articles.json'
    data = load_json(path)
    if not isinstance(data, dict) or not isinstance(data.get('articles'), list):
        return
    kept = [row for row in data['articles']
            if not (isinstance(row, dict) and str(row.get('path', '')) == name)]
    if len(kept) == len(data['articles']):
        return
    data['articles'] = kept
    try:
        path.write_text(json.dumps(data, indent=2), encoding='utf-8')
    except OSError:
        pass


def _read_nested_page(tree: Path, name: str) -> str | None:
    """One page of a content tree, addressed by a `/`-separated path, or None.

    Each path segment must match `_NAME_RE` (word characters and hyphens only), so `..`
    and absolute segments are rejected before any filesystem access; the resolved target is
    then confirmed to stay within *tree* as defence in depth against symlink escapes."""
    if name.endswith('.md'):                       # a rewritten cross-link that kept its suffix
        name = name[:-3]
    parts = name.split('/')
    if not parts or any(not _NAME_RE.fullmatch(part) for part in parts):
        return None
    target = tree.joinpath(*parts).with_suffix('.md')
    try:
        if not target.resolve().is_relative_to(tree.resolve()):
            return None
        return target.read_text(encoding='utf-8')
    except OSError:
        return None


#: The per-tag skeleton pages live under these folders (one page per tag, reached by its
#: chip). The problem page's "Topics" list shows curated topics — everything *else*.
_FACET_FOLDERS = ('domain', 'technique', 'takeaway')
_ARTICLE_TAGS_RE = re.compile(r'<!--\s*tags:\s*\[(.*?)\]\s*-->', re.DOTALL)


def _declared_tags(text: str) -> set[str]:
    """The tag slugs an article declares in its `<!-- tags: [...] -->` comment."""
    m = _ARTICLE_TAGS_RE.search(text)
    return {s.strip() for s in m.group(1).split(',') if s.strip()} if m else set()


def problem_tag_view(repo_root: Path, number: int) -> dict[str, Any]:
    """The tag/topic view model for a problem page.

    Reads the problem's `tags.json` and the central vocabulary, and returns the tags grouped
    by facet (techniques keyed to each solution index) as chips — each with the `/topics` URL
    of its per-tag page when one exists — plus `flat` for the header row and `topics`, the
    curated topic pages (outside the per-tag facet folders) that cover any of the problem's tags.
    """
    tags = load_json(solution_dir(repo_root, number) / 'tags.json')
    if not isinstance(tags, dict):
        return {'has_tags': False}
    vocab = {t['slug']: t for t in (load_json(repo_root / 'topics' / 'tags.json') or {}).get('tags', [])}
    topics_root = repo_root / 'topics'

    def chip(slug: str, facet: str) -> dict[str, Any]:
        page = topics_root / facet / f'{slug}.md'
        return {'slug': slug, 'name': vocab.get(slug, {}).get('name', slug),
                'facet': facet, 'url': f'/topics/{facet}/{slug}' if page.is_file() else None}

    domain = [chip(s, 'domain') for s in tags.get('domain', [])]
    takeaways = [chip(s, 'takeaway') for s in tags.get('takeaways', [])]
    techniques = [{'index': idx, 'tags': [chip(s, 'technique') for s in slugs]}
                  for idx, slugs in sorted(tags.get('techniques', {}).items()) if slugs]
    # `flat` (the header row) is the distinct tag set; a technique shared across indices
    # appears once. The per-index repetition lives only in `techniques` (the workbench).
    seen: set[str] = set()
    flat: list[dict[str, Any]] = []
    for c in domain + [t for grp in techniques for t in grp['tags']] + takeaways:
        if c['slug'] not in seen:
            seen.add(c['slug'])
            flat.append(c)
    own = seen

    topics: list[DocEntry] = []
    if own:
        for path in sorted(topics_root.rglob('*.md')):
            rel = path.relative_to(topics_root)
            if rel.parts[0] in _FACET_FOLDERS:            # a per-tag skeleton — reached via its chip
                continue
            try:
                text = path.read_text(encoding='utf-8')
            except OSError:
                continue
            if own & _declared_tags(text):
                name = rel.with_suffix('').as_posix()
                topics.append(DocEntry(name=name, heading=name, title=_page_title(text, path.stem)))
    return {'has_tags': bool(flat), 'flat': flat, 'domain': domain,
            'techniques': techniques, 'takeaways': takeaways, 'topics': topics}

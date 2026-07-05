#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""aiohttp application: the SolverShell terminal, its PTY WebSocket, and the viewer.

`build_app` wires one localhost server with three concerns:

- **Terminal** — `GET /` serves the xterm.js page (the default landing page) and
  `GET /ws` attaches to the signed-in user's persistent `solver` shell on a
  pseudo-terminal (see :class:`solver.web.pty_manager.PersistentPty`). Binary WS
  frames are raw terminal bytes both ways; a `{"resize": [cols, rows]}` text frame
  propagates geometry. There is at most one shell per user — extra tabs attach to
  the same shell — and it survives disconnect, ending only on `logout`, an
  in-shell `exit`, or server stop.

- **Read-only viewer** — the static summary/problem pages plus the problem files
  read directly from each problem's solution directory (`problem.solution_dir`).
  `GET /active-problem` reports the signed-in user's active problem — the number
  their `solver` shell holds in `variables.problem` — so the header can wire its
  "Active problem" link on pages that carry no problem number in the URL.

- **Guides** — `GET /index` serves the guides index (the default left-pane content),
  and `GET /docs/<name>` renders a `docs/` Markdown guide to HTML (markdown-it-py,
  with heading anchors matching `update_doc.py` and code highlighted client-side).

- **Code editor** — `GET /edit/<n>/<file>` serves the editable code editor for a
  solution file (the read-only viewer above never edits); `POST /edit/<n>/<file>`
  validates and saves it, `DELETE /edit/<n>/<file>` removes it, and `POST /edit/lint`
  lints an unsaved buffer.

- **Edits** — `POST /cmd` dispatches a shell command line to the signed-in user's
  web shell (it runs in their live PTY session, output streaming to the terminal),
  and `POST /progress` saves the progress file.
"""
from __future__ import annotations

__all__ = ['build_app']

import asyncio
import functools
import html
import json
import mimetypes
import re
import tempfile
from pathlib import Path
from subprocess import run
from typing import Any, Callable

from aiohttp import WSCloseCode, WSMsgType, web
from aiohttp.typedefs import Handler
from markdown_it import MarkdownIt

from solver.config import config
from solver.core.problems import Problem, problems
from solver.shell.command import is_authorized_for
from solver.shell.variables import variables
from solver.utils.identity import slugify
from solver.utils.summary import summary
from solver.web.auth.routes import USER_EMAIL, WS_CONNECTIONS, auth_middleware, profile_for, setup_auth
from solver.web.pty_manager import PTY_MANAGER, setup_pty_manager

#: Top-level static page assets served verbatim from `config.static_file_dir`.
_STATIC_ASSETS: frozenset[str] = frozenset({
    'code.css', 'code.html', 'code.js', 'common.css', 'favicon.svg',
    'header.js', 'index.css', 'docs.css', 'problem.css', 'problem.html', 'problem.js', 'problems.json',
    'solver.css', 'solver-theme.css', 'solver.html', 'solver.js', 'summary.css',
    'summary.html', 'summary.js',
    'login.css', 'login.js', 'srp-client.js', 'register.css', 'register.js',
    'password.css', 'password.js',
})

#: Markdown renderer for the docs/ guides (GitHub-flavoured: tables + strikethrough).
_MD = MarkdownIt('commonmark').enable(['table', 'strikethrough'])

#: mime type of a served problem file → highlight.js language for the code viewer.
_CODE_LANGUAGES: dict[str, str] = {
    'text/x-python': 'python',
    'text/x-csrc': 'c',
}

#: file suffix → editor language label for the `/edit/<n>/<file>` code-editor view
#: (`_edit_file`). Governs syntax highlighting and, in code.js, whether the file is
#: editable; an unlisted suffix opens read-only as plain text.
_EDIT_LANGUAGES: dict[str, str] = {
    '.py': 'python', '.c': 'c', '.json': 'json', '.html': 'html',
}


def requires(capability: str) -> Callable[[Handler], Handler]:
    """Gate a route by the requester's profile against a ``commands.csv`` capability.

    The web mutating routes (file save/delete, the code editor, lint, progress save)
    act directly on the solution tree rather than through the profile-gated shell, so
    they need the same authorization enforced here. *capability* is a command name;
    a profile that may run that command in the shell may use the route, keeping
    ``commands.csv`` the single source of truth for both surfaces. The check resolves
    the *requesting* user's profile (the server process itself runs as admin), and a
    disallowed profile gets 403 (it is authenticated — just not permitted).

    Read-only routes and the terminal (``/ws``, ``/cmd``) are intentionally left
    ungated: the terminal is any authenticated user's, and the shell restricts the
    commands it will run there by the same policy.
    """
    def wrap(handler: Handler) -> Handler:
        @functools.wraps(handler)
        async def guarded(request: web.Request) -> web.StreamResponse:
            if not is_authorized_for(capability, profile_for(request)):
                raise web.HTTPForbidden(text=f'{capability}: not permitted for your profile')
            return await handler(request)
        return guarded
    return wrap


# ---------------------------------------------------------------------------
# Static + terminal
# ---------------------------------------------------------------------------
async def _serve_static(request: web.Request) -> web.StreamResponse:
    """Serve a known top-level static page asset (404 for anything else)."""
    name = request.match_info.get('asset') or 'summary.html'
    if name not in _STATIC_ASSETS:
        raise web.HTTPNotFound()
    if (file := config.static_file_dir / name).exists():
        return web.FileResponse(file)
    if (file := config.static_file_dir / file.stem / name).exists():
        return web.FileResponse(file)
    raise web.HTTPNotFound()


async def _serve_favicon(request: web.Request) -> web.StreamResponse:
    """Serve the SVG favicon for the default `/favicon.ico` browser request."""
    return web.FileResponse(config.static_file_dir / 'favicon.svg')


async def _serve_landing_page(request: web.Request) -> web.StreamResponse:
    """Serve the xterm.js terminal page (the default landing page at `/`)."""
    return web.FileResponse(config.static_file_dir / 'solver/solver.html')


async def _serve_summary_page(request: web.Request) -> web.StreamResponse:
    """Serve the solutions summary page (`/summary`)."""
    return web.FileResponse(config.static_file_dir / 'summary/summary.html')


async def _serve_index_page(request: web.Request) -> web.StreamResponse:
    """Serve the guides index — the default left-pane content (`GET /index`)."""
    return web.FileResponse(config.static_file_dir / 'index/index.html')


def _doc_slug(text: str) -> str:
    """GitHub-style heading slug — matches `update_doc.py`'s catalogue anchors, so a
    guide's `commands-index.md#command-…` links resolve to the rendered headings."""
    return re.sub(r'[^a-z0-9 -]+', '', text.lower()).strip(' ').replace(' ', '-').strip('-')


def _render_markdown(text: str) -> str:
    """Render a guide's Markdown to HTML: slugged heading ids + intra-doc links rewired.

    Each heading gets the same slug `update_doc.py` assumes, so in-page and cross-doc
    `#anchor` links land; relative `foo.md` (or `docs/foo.md`) links are rewritten to
    the `/docs/` route.
    """
    tokens = _MD.parse(text)
    for i, token in enumerate(tokens):
        if token.type == 'heading_open':
            token.attrSet('id', _doc_slug(tokens[i + 1].content))
    rendered = _MD.renderer.render(tokens, _MD.options, {})
    return re.sub(r'href="(?:docs/)?([\w-]+)\.md(#[^"]*)?"', r'href="/docs/\1\2"', rendered)


async def _serve_doc(request: web.Request) -> web.StreamResponse:
    """Render a `docs/` Markdown guide as an HTML page (`GET /docs/<name>`).

    *name* is a guide stem (an optional `.md` suffix is stripped, so a rewritten
    `foo.md` cross-link resolves); anything that is not a bare `[\\w-]+` name, or a
    guide that does not exist, is 404. The rendered HTML is injected into the docs
    viewer template, which highlights code client-side (highlight.js).
    """
    name = request.match_info['name']
    if name.endswith('.md'):
        name = name[:-3]
    if not re.fullmatch(r'[\w-]+', name):
        raise web.HTTPNotFound()
    try:
        text = (config.docs_dir / f'{name}.md').read_text(encoding='utf-8')
    except (FileNotFoundError, OSError):
        raise web.HTTPNotFound()
    template = (config.static_file_dir / 'docs/docs.html').read_text(encoding='utf-8')
    page = template.replace('{{TITLE}}', html.escape(name)).replace('{{CONTENT}}', _render_markdown(text))
    return _bytes_response(page.encode('utf-8'), 'text/html')


# ---------------------------------------------------------------------------
# AI reference pages — collate several sources into one rendered view (`/ai/<name>`)
# ---------------------------------------------------------------------------
#: The claude-euler-solver skill definition.
_SKILL_MD: Path = config.root_dir / 'solver/ai/claude/skills/claude-euler-solver/SKILL.md'
#: The convention guides (shared by the skill and the API prompts), in reading order.
_AI_CONVENTIONS: tuple[str, ...] = (
    'convention_python_solution', 'convention_c_translation',
    'convention_source_documentation', 'convention_documentation', 'convention_test_cases',
)

_AI_SKILL_INTRO = """\
# AI · Euler Solver skill

The **claude-euler-solver** skill runs Claude Code **headless** against a single
problem's solution files. The shell's `claude-skill` command launches it as
`claude -p /claude-euler-solver <problem_number> <action>` — `<action>` is `solve`
or `review` — and Claude edits the solution directory directly, prints a short
summary, and ends the turn. The standards it must meet are the shared
[conventions](/ai/conventions). Below is the skill definition verbatim.
"""

_AI_API_INTRO = """\
# AI · generation prompts

The shell's `claude-api` command generates solution artifacts — Python and C code,
`notes.html`, and `test_cases.json` — through the Claude API rather than an
interactive agent. Each target is produced from a **prompt template** in
`solver/templates/`, rendered by `engine.py` with the problem statement, the current
solution files, and the shared [conventions](/ai/conventions) substituted in. Below
are those prompt templates verbatim.
"""

_AI_CONVENTIONS_INTRO = """\
# AI · conventions

The standards every generated solution must meet, shared by both AI paths: the
[skill](/ai/skill) reads them before acting, and each is injected into the matching
[API](/ai/api) prompt. They are the single source of truth for their slice of a
solution — the Python `solve()`, the C port, in-source documentation, `notes.html`,
and `test_cases.json`. All are collated below.
"""


def _strip_frontmatter(text: str) -> str:
    """Drop a leading YAML front-matter block so it does not render as body text."""
    return re.sub(r'\A---\n.*?\n---\n', '', text, count=1, flags=re.DOTALL)


def _compose_skill_page() -> str:
    """Intro + the SKILL.md definition (front-matter stripped)."""
    return _AI_SKILL_INTRO + '\n---\n\n' + _strip_frontmatter(_SKILL_MD.read_text(encoding='utf-8'))


def _fence(content: str) -> str:
    """Wrap *content* in a `text` code fence long enough to survive backticks inside it."""
    longest = max((len(run) for run in re.findall(r'`+', content)), default=0)
    ticks = '`' * max(3, longest + 1)
    return f'{ticks}text\n{content}\n{ticks}'


def _compose_api_page() -> str:
    """Intro + every `prompt_*.txt` template, each fenced verbatim under its filename."""
    parts = [_AI_API_INTRO]
    for path in sorted(config.templates_dir.glob('prompt_*.txt')):
        parts.append(f'## `{path.name}`\n\n' + _fence(path.read_text(encoding='utf-8').strip()))
    return '\n---\n\n'.join(parts)


def _compose_conventions_page() -> str:
    """Intro + every convention guide, collated."""
    parts = [_AI_CONVENTIONS_INTRO]
    parts += [(config.docs_dir / f'{name}.md').read_text(encoding='utf-8') for name in _AI_CONVENTIONS]
    return '\n---\n\n'.join(parts)


#: Composed AI pages keyed by the `/ai/<name>` path segment.
_AI_PAGES: dict[str, Callable[[], str]] = {
    'skill': _compose_skill_page,
    'api': _compose_api_page,
    'conventions': _compose_conventions_page,
}


async def _serve_ai_page(request: web.Request) -> web.StreamResponse:
    """Render a composed AI reference page (`GET /ai/<name>`, name in {skill, api, conventions}).

    Collates several source files (the skill, the API prompt templates, or the
    convention guides) into a single view, reusing the docs viewer template.
    """
    composer = _AI_PAGES.get(request.match_info['name'])
    if composer is None:
        raise web.HTTPNotFound()
    template = (config.static_file_dir / 'docs/docs.html').read_text(encoding='utf-8')
    page = template.replace('{{TITLE}}', html.escape(request.match_info['name'])).replace(
        '{{CONTENT}}', _render_markdown(composer()))
    return _bytes_response(page.encode('utf-8'), 'text/html')


def _active_problem(email: str) -> int:
    """The signed-in user's active problem number — their shell's `variables.problem`.

    The `solver` shell persists `variables.problem` to a per-user `last_problem`
    file whenever it changes (see `solver.shell.shell.SolverShell` and
    `solver.shell.variables`); this reads that file for *email*'s slug. A missing,
    unparseable, or unknown number falls back to `variables.problem` here — which,
    unset in the web process, yields the last solved problem, matching the shell's
    own default.
    """
    path = config.state_dir / slugify(email) / config.last_problem_file.name
    try:
        return Problem.from_number(int(path.read_text(encoding='utf-8').strip())).number
    except (OSError, ValueError):
        return variables.problem.number


async def _serve_active_problem(request: web.Request) -> web.StreamResponse:
    """Report the signed-in user's active problem (`GET /active-problem`).

    Replies `{"problem": <number>}`; the header wires its "Active problem" link
    from it on pages that carry no problem number in the URL (summary, progress,
    the shell), replacing the former browser cookie.
    """
    return web.json_response({'problem': _active_problem(request[USER_EMAIL])})


async def _serve_progress_page(request: web.Request) -> web.StreamResponse:
    """Serve the progress file in the shared code editor (`GET /edit/progress`).

    The progress file (`config.static_file_progress`) lives outside the solution
    tree; it renders through the same code editor as solution files — an editable
    HTML buffer that saves back to `/edit/progress` (`_save_progress_page`).
    """
    progress_file = config.static_file_progress
    try:
        content: bytes = progress_file.read_bytes()
    except (FileNotFoundError, KeyError, ValueError, IsADirectoryError):
        raise web.HTTPNotFound()
    edit_language = _EDIT_LANGUAGES.get(Path(progress_file.name).suffix, '')
    return _bytes_response(_render_code_page(progress_file.name, content, edit_language), 'text/html')


def _save_progress(content: bytes) -> tuple[int, str]:
    """Write edited progress content, rolling back if it no longer parses; return (status, message).

    The progress file is outside the solution tree, so no per-problem checks apply.
    After writing, `summary()` re-parses it into problems.json; if that fails the
    previous bytes are restored so a broken edit never lands (status mirrors HTTP).
    """
    progress_file = config.static_file_progress
    previous = progress_file.read_bytes() if progress_file.is_file() else b''
    progress_file.write_bytes(content)
    if summary() != 0:
        progress_file.write_bytes(previous)
        return 400, 'invalid progress — rolled back'
    return 200, f'saved {progress_file.name}'


@requires('summary')
async def _save_progress_page(request: web.Request) -> web.StreamResponse:
    """Save the edited progress file (`POST /edit/progress`)."""
    body = await request.read()
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, _save_progress, body)
    return _text(*result)


async def _serve_vendor_asset(request: web.Request) -> web.StreamResponse:
    """Serve a vendored front-end asset under `web-content/vendor/`.

    The filename is resolved under the vendor directory; anything that escapes it
    (`..` etc.) or is absent is rejected as 404.
    """
    vendor_dir = (config.static_file_dir / 'vendor').resolve()
    target = (vendor_dir / request.match_info['filename']).resolve()
    if vendor_dir not in target.parents or not target.is_file():
        raise web.HTTPNotFound()
    return web.FileResponse(target)


def _parse_resize(payload: str) -> tuple[int, int] | None:
    """Parse a `{"resize": [cols, rows]}` control frame; None if it is not one."""
    try:
        message: Any = json.loads(payload)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    resize = message.get('resize') if isinstance(message, dict) else None
    if (isinstance(resize, list) and len(resize) == 2
            and all(isinstance(n, int) for n in resize)):
        cols, rows = resize
        return cols, rows
    return None


async def _ws_handler(request: web.Request, save: bool) -> web.WebSocketResponse:
    """Attach a browser terminal to the signed-in user's persistent `solver` shell.

    The shell is forked on first connect and reused thereafter (one per user);
    the recent output buffer is replayed so a reconnecting terminal redraws its
    prompt. The socket is tracked by email so `logout` can close it, and detached
    on disconnect *without* killing the shell. Binary frames are forwarded to the
    PTY as keystrokes; a `resize` text frame propagates the browser geometry.
    """
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    email: str = request[USER_EMAIL]  # set by auth_middleware (the /ws route is gated)
    connections = request.app[WS_CONNECTIONS]
    connections.setdefault(email, set()).add(ws)

    pty = request.app[PTY_MANAGER].get_or_create(email, save=save)
    await pty.attach(ws)
    try:
        async for msg in ws:
            if msg.type == WSMsgType.BINARY:
                pty.write(msg.data)
            elif msg.type == WSMsgType.TEXT:
                if (size := _parse_resize(msg.data)) is not None:
                    pty.resize(cols=size[0], rows=size[1])
            elif msg.type == WSMsgType.ERROR:
                break
    finally:
        pty.detach(ws)  # the shell keeps running; only this socket goes away
        if (live := connections.get(email)) is not None:
            live.discard(ws)
            if not live:
                connections.pop(email, None)
    return ws


# ---------------------------------------------------------------------------
# Viewer helpers
# ---------------------------------------------------------------------------
def _prettify_json(content: bytes) -> bytes:
    """Re-serialise JSON with two-space indentation for the code viewer.

    Returns the original bytes unchanged if they are not valid JSON, so a
    malformed file is still shown rather than swallowed.
    """
    try:
        parsed = json.loads(content)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return content
    return json.dumps(parsed, indent=2, ensure_ascii=False).encode('utf-8')


def _render_code_page(filename: str, content: bytes, language: str) -> bytes:
    """Wrap source code in the code.html viewer (syntax highlighting + line numbers).

    The source is HTML-escaped and embedded directly in the page, so the browser
    renders it like an IDE rather than downloading raw text.
    """
    template = (config.static_file_dir / 'code/code.html').read_bytes()
    page = (template.decode('utf-8')
            .replace('{{FILENAME}}', html.escape(filename))
            .replace('{{LANGUAGE}}', language)
            .replace('{{CODE}}', html.escape(content.decode('utf-8', errors='replace'))))
    return page.encode('utf-8')


def _validate_source(path: Path) -> tuple[bool, str]:
    """Validate a Python or C source file on disk; return (ok, captured diagnostics).

    Python is checked with flake8, C is compiled with the runner-aware build script.
    Both capture stdout/stderr so diagnostics can be returned to the editor verbatim.
    """
    if path.suffix == '.py':
        proc = run(['flake8', f'--max-line-length={config.max_line_length}', str(path)],
                   cwd=config.root_dir, capture_output=True, text=True)
    elif path.suffix == '.c':
        proc = run(f'{config.scripts.compile_c} {path}', shell=True,
                   cwd=config.root_dir, capture_output=True, text=True)
    else:
        return False, 'not implemented code validation for this file type'
    if proc.returncode == 0:
        return True, ''
    return False, (proc.stdout + ('\n' if proc.stdout and proc.stderr else '') + proc.stderr).strip()


def _save_content(problem_number: int, filename: str, content: bytes) -> tuple[int, str]:
    """Validate edited content and write it into the solution directory; return (status, message).

    Status mirrors HTTP — 200 saved, 400 on a bad request or failed validation.
    JSON is parsed, Python is flake8-linted, and C is compiled before the file is
    accepted; on any validation failure the previous content is restored so a bad
    edit never lands.
    """
    if Path(filename).name != filename or Path(filename).suffix not in ('.py', '.c', '.json', '.html'):
        return 400, f'{filename} is not an editable solution file'
    try:
        problem: Problem = Problem.from_number(problem_number)
    except ValueError:
        return 400, f'problem {problem_number} not found'
    target: Path = problem.solution_dir.joinpath(filename)
    if filename.endswith('.json'):
        try:
            json.loads(content)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            return 400, f'invalid JSON: {exc}'
        target.write_bytes(content)
        return 200, f'saved {filename}'
    if filename.endswith('.html'):
        # HTML stubs (notes / statement) have no validator — write them verbatim.
        target.write_bytes(content)
        return 200, f'saved {filename}'
    previous: bytes = target.read_bytes()
    target.write_bytes(content)
    ok, message = _validate_source(target)
    if not ok:
        target.write_bytes(previous)  # reject: never leave a broken file behind
        return 400, message or f'{filename} failed validation'
    return 200, f'saved {filename}'


#: flake8 line: `path:row:col: CODE message`.
_FLAKE8_RE = re.compile(r'^.*?:(\d+):(\d+):\s+([A-Z]\d+)\s+(.*)$')
#: gcc/clang line: `path:row[:col]: error|warning|note: message`.
_GCC_RE = re.compile(r'^.*?:(\d+):(?:(\d+):)?\s+(error|warning|note):\s+(.*)$')


def _parse_diagnostics(output: str, suffix: str) -> list[dict[str, Any]]:
    """Parse flake8 / gcc text into `{line, col, severity, message}` diagnostics.

    Non-matching lines (summary banners, multi-line context) are ignored. flake8
    `F*` / `E9*` (pyflakes + syntax) map to errors, the rest to warnings; gcc maps
    by the emitted severity word (a `note` becomes a warning).
    """
    diagnostics: list[dict[str, Any]] = []
    if suffix == '.py':
        for line in output.splitlines():
            if (m := _FLAKE8_RE.match(line)) is None:
                continue
            row, col, code, message = m.groups()
            severity = 'error' if code[0] == 'F' or code.startswith('E9') else 'warning'
            diagnostics.append({'line': int(row), 'col': int(col),
                                'severity': severity, 'code': code, 'message': message})
    else:  # .c
        for line in output.splitlines():
            if (m := _GCC_RE.match(line)) is None:
                continue
            row, col, severity, message = m.groups()
            diagnostics.append({'line': int(row), 'col': int(col or 1),
                                'severity': 'warning' if severity == 'note' else severity,
                                'message': message})
    return diagnostics


def _lint_content(filename: str, content: bytes) -> tuple[int, str]:
    """Lint edited content without saving it; return (status, JSON diagnostics).

    Runs the same validators as save — flake8 for Python, the runner-aware compile
    for C — against a throwaway temp copy, so the solution file is never touched
    and a syntactically broken buffer is still diagnosable. The reply is
    `{"diagnostics": [{line, col, severity, message, code?}, ...]}` (empty when clean).
    """
    suffix = Path(filename).suffix
    if Path(filename).name != filename or suffix not in ('.py', '.c'):
        return 400, json.dumps({'diagnostics': []})
    with tempfile.TemporaryDirectory() as tmp:
        tmp_file = Path(tmp) / f'lint{suffix}'  # compile.sh finds runner.h via an absolute -I
        tmp_file.write_bytes(content)
        ok, message = _validate_source(tmp_file)
    diagnostics = [] if ok else _parse_diagnostics(message, suffix)
    return 200, json.dumps({'diagnostics': diagnostics})


def _del_solution(problem_number: int, filename: str) -> tuple[int, str]:
    """Delete a solution from its solution directory; return (status, message)."""
    if Path(filename).name != filename or Path(filename).suffix not in ('.py', '.c'):
        return 400, f'{filename} is not a deletable solution file'
    try:
        problem: Problem = Problem.from_number(problem_number)
    except ValueError:
        return 200, f'deleted {filename}'
    target: Path = problem.solution_dir.joinpath(filename)
    target.unlink(missing_ok=True)
    return 200, f'deleted {filename}'


# ---------------------------------------------------------------------------
# Viewer routes
# ---------------------------------------------------------------------------
def _wants_html_view(request: web.Request) -> bool:
    """True when the request is a browser navigation, not a programmatic fetch.

    A navigation's Accept header lists text/html; problem.js's fetchJson sends
    Accept: application/json. Requiring text/html AND the absence of an explicit
    application/json keeps the raw representation the safe default for any other
    caller (curl, plain fetch with Accept: */*).
    """
    accept = request.headers.get('Accept', '')
    return 'text/html' in accept and 'application/json' not in accept


def _bytes_response(body: bytes, content_type: str) -> web.Response:
    """A no-cache byte response with an explicit content type."""
    return web.Response(body=body, content_type=content_type, charset='utf-8',
                        headers={'Cache-Control': 'no-cache'})


def _render_json(request: web.Request, filename: str, content: bytes) -> web.Response:
    """Serve JSON content: the code viewer for a browser navigation, raw bytes otherwise."""
    if _wants_html_view(request):
        return _bytes_response(_render_code_page(filename, _prettify_json(content), 'json'), 'text/html')
    return _bytes_response(content, 'application/json')


async def _problem_page(request: web.Request) -> web.StreamResponse:
    """Serve the problem viewer page for `/<n>/`."""
    return web.FileResponse(config.static_file_dir / 'problem/problem.html')


async def _redirect_with_slash(request: web.Request) -> web.StreamResponse:
    """Redirect `/<n>` to `/<n>/` so relative fetches resolve under the problem."""
    raise web.HTTPMovedPermanently(f'/{request.match_info["problem_number"]}/')


def _resolve_solution_file(request: web.Request) -> tuple[Problem, str]:
    """Validate the route's `<problem_number>`/`<filename>` and return (problem, filename).

    Rejects path traversal and an out-of-range or unknown problem with 404. The file
    itself need not exist — the caller reads it. Shared by the read-only viewer
    (`_problem_file`) and the editor (`_edit_file`).
    """
    problem_number = int(request.match_info['problem_number'])
    filename = request.match_info['filename']
    if '..' in Path(filename).parts:  # filename may hold a subdir (resources/…); reject traversal
        raise web.HTTPNotFound()
    if problem_number < 1 or problem_number > problems.last_problem.number:
        raise web.HTTPNotFound()
    try:
        return Problem.from_number(problem_number), filename
    except ValueError:
        raise web.HTTPNotFound()


async def _problem_file(request: web.Request) -> web.StreamResponse:
    """Serve a single problem file, read-only, for `/<n>/<filename>`.

    `solutions` is the synthesised solution listing; source files render through
    the code viewer on a browser navigation; JSON gets the viewer only when a human
    is navigating (problem.js fetches with Accept: application/json for raw bytes).
    Editing lives under `/edit/<n>/<filename>` (`_edit_file`), not here.
    """
    problem, filename = _resolve_solution_file(request)
    if filename == 'solutions':
        files: list[str] = []
        for file in problem.solution_dir.glob(f'p{problem.number:04d}_s*.*'):
            files.append(f'{file.stem}_c' if file.suffix == '.c' else file.name)
        return _render_json(request, 'solutions', json.dumps(sorted(files), indent=2).encode('utf-8'))
    try:
        content: bytes = problem.solution_dir.joinpath(filename).read_bytes()
    except (FileNotFoundError, KeyError, ValueError):
        if _wants_html_view(request):
            content = f'Error: file {filename} not found!'.encode('utf-8')
        else:
            raise web.HTTPNotFound()
    mime, _ = mimetypes.guess_type(filename)
    language = _CODE_LANGUAGES.get(mime or '')
    if language is not None:
        return _bytes_response(_render_code_page(filename, content, language), 'text/html')
    if mime == 'application/json':
        return _render_json(request, filename, content)
    return _bytes_response(content, mime or 'application/octet-stream')


async def _edit_file(request: web.Request) -> web.StreamResponse:
    """Serve the editable code editor for a solution file (`GET /edit/<n>/<filename>`).

    The counterpart to `_problem_file`, which is always read-only: this always
    renders the code editor for the file — including the HTML stubs (notes /
    statement) that otherwise render — with the Save / Eval / Del buttons that the
    sibling `/edit/...` write routes back. The suffix picks the editor language; an
    unknown one opens read-only as plain text. A missing file is 404 (`edit` only
    opens existing files; use `new` to create one first).
    """
    problem, filename = _resolve_solution_file(request)
    try:
        content: bytes = problem.solution_dir.joinpath(filename).read_bytes()
    except (FileNotFoundError, KeyError, ValueError, IsADirectoryError):
        raise web.HTTPNotFound()
    edit_language = _EDIT_LANGUAGES.get(Path(filename).suffix, '')
    return _bytes_response(_render_code_page(filename, content, edit_language), 'text/html')


def _text(code: int, message: str) -> web.Response:
    """A plain-text response with the given HTTP status."""
    return web.Response(status=code, text=message, content_type='text/plain', charset='utf-8')


@requires('edit')
async def _save_problem_file(request: web.Request) -> web.StreamResponse:
    """Save an edited solution file (`POST /edit/<n>/<filename>`)."""
    problem_number = int(request.match_info['problem_number'])
    filename = request.match_info['filename']
    body = await request.read()
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, _save_content, problem_number, filename, body)
    return _text(*result)


@requires('edit')
async def _delete_problem_file(request: web.Request) -> web.StreamResponse:
    """Delete a solution (`DELETE /edit/<n>/<filename>`)."""
    problem_number = int(request.match_info['problem_number'])
    filename = request.match_info['filename']
    result = _del_solution(problem_number, filename)
    return _text(*result)


async def _run_command(request: web.Request, save: bool) -> web.StreamResponse:
    """Dispatch a shell command to the signed-in user's web shell (`POST /cmd`).

    Body: `{"command": "<shell command line>"}`. The line is written to the user's
    persistent PTY shell — created if none is attached yet — as if typed at the
    prompt, so it runs in their live session and its output streams to the terminal
    panel, exactly as the terminal page achieves by writing to its `/ws` socket
    directly (a page with a shell can wire the button either way). The shell owns
    the run, so the reply is just `{"dispatched": "<command>"}`; 400 for a malformed
    body.
    """
    email: str = request[USER_EMAIL]
    try:
        data = await request.json()
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise web.HTTPBadRequest()
    if not isinstance(data, dict) or not isinstance(data.get('command'), str):
        raise web.HTTPBadRequest()
    command = data['command'].strip()
    if not command:
        raise web.HTTPBadRequest()
    pty = request.app[PTY_MANAGER].get_or_create(email, save=save)
    pty.write((command + '\n').encode('utf-8'))
    return web.json_response({'dispatched': command})


@requires('lint')
async def _lint_file(request: web.Request) -> web.StreamResponse:
    """Lint an edited (unsaved) solution file (`POST /edit/lint`).

    Body: `{"filename": "p0007_s0.py", "content": "<source>"}` — the linter keys off
    the filename's suffix, so no problem number is needed. Replies with JSON
    `{"diagnostics": [...]}` the editor renders as inline squiggles; 400 for a
    malformed body.
    """
    try:
        data = await request.json()
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise web.HTTPBadRequest()
    if not isinstance(data, dict) or not isinstance(data.get('filename'), str):
        raise web.HTTPBadRequest()
    content = str(data.get('content', '')).encode('utf-8')
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, _lint_content, data['filename'], content)
    code, payload = result
    return web.Response(status=code, text=payload, content_type='application/json', charset='utf-8')


async def _close_all_sockets(app: web.Application) -> None:
    """on_shutdown hook: close every attached terminal WebSocket up front.

    aiohttp's graceful shutdown fires `on_shutdown` first, then blocks up to its
    `shutdown_timeout` waiting for in-flight request handlers to return, and only
    then fires `on_cleanup` (where `_close_all_ptys` reaps the shells). The `/ws`
    handler sits in `async for msg in ws`, which ends only when its socket closes
    — so without this the server stalls on that wait for the full timeout whenever
    a terminal is attached. Closing the sockets here ends those loops at once,
    letting the handlers return before the wait; the persistent shells behind them
    are still torn down later on `on_cleanup`.
    """
    connections = app[WS_CONNECTIONS]
    sockets = [ws for group in connections.values() for ws in group]
    connections.clear()
    for ws in sockets:
        try:
            await ws.close(code=WSCloseCode.GOING_AWAY, message=b'server shutdown')
        except Exception:  # noqa: BLE001 — best-effort teardown
            pass


def build_app(save: bool) -> web.Application:
    """Construct the aiohttp application: terminal, WebSocket, and read-only viewer.

    Every route is gated by :func:`solver.web.auth.routes.auth_middleware` except
    the login page, its assets, and the SRP endpoints; :func:`setup_auth` wires the
    session store and those routes onto the app.
    """
    app = web.Application(middlewares=[auth_middleware])
    setup_auth(app)
    setup_pty_manager(app)
    app.on_shutdown.append(_close_all_sockets)
    ws_handler = functools.partial(_ws_handler, save=save)
    # Routes are ordered by path, with the methods that share a path kept together.
    # The dynamic routes are disjoint by regex (digits / extensions / segment counts),
    # and every literal path precedes the `/{asset}` and `/{problem_number}` catch-alls,
    # so this ordering is unambiguous for aiohttp's first-match dispatch.
    app.add_routes([
        web.get('/', _serve_landing_page),  # terminal (landing page)
        web.get('/active-problem', _serve_active_problem),
        web.post('/cmd', functools.partial(_run_command, save=save)),  # dispatch to the web shell
        web.get(r'/ai/{name}', _serve_ai_page),  # a composed AI reference page (skill / api / conventions)
        web.get(r'/docs/{name}', _serve_doc),  # a rendered docs/ Markdown guide
        web.post('/edit/lint', _lint_file),  # stateless lint (suffix-keyed)
        web.get('/edit/progress', _serve_progress_page),
        web.post('/edit/progress', _save_progress_page),
        web.get(r'/edit/{problem_number:\d+}/{filename:.+}', _edit_file),  # code editor + its writes
        web.post(r'/edit/{problem_number:\d+}/{filename:.+}', _save_problem_file),
        web.delete(r'/edit/{problem_number:\d+}/{filename:.+}', _delete_problem_file),
        web.get('/favicon.ico', _serve_favicon),
        web.get('/index', _serve_index_page),  # guides index (default left-pane content)
        web.get('/summary', _serve_summary_page),
        web.get(r'/vendor/{filename:.+}', _serve_vendor_asset),  # vendored editor JS/CSS/etc.
        web.get('/ws', ws_handler),  # terminal WebSocket
        web.get(r'/{asset:[A-Za-z0-9_.-]+\.(?:css|js|html|json|svg)}', _serve_static),
        web.get(r'/{problem_number:\d+}', _redirect_with_slash),  # read-only problem viewer
        web.get(r'/{problem_number:\d+}/', _problem_page),
        web.get(r'/{problem_number:\d+}/{filename:.+}', _problem_file),
    ])
    return app

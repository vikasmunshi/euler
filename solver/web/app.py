#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""aiohttp application: the SolverShell terminal, its PTY WebSocket, and the viewer.

`build_app` wires one localhost server with three concerns:

- **Terminal** — `GET /` serves the xterm.js page (the default landing page) and
  `GET /ws` streams a
  single interactive `solver` shell on a pseudo-terminal (see
  :class:`solver.web.pty_bridge.PtySession`). Binary WS frames are raw terminal
  bytes both ways; a `{"resize": [cols, rows]}` text frame propagates geometry.
  Only one PTY session is allowed at a time — every session drives the shared
  `workspace/` and concurrent shells would race on it.

- **Read-only viewer** — the static summary/problem pages plus the problem files
  served through :func:`solver.core.stack.read_stack_file` (decrypting as needed,
  preferring the live workspace copy when a problem is active). The browser learns
  the workspace state from `GET /flags?problem_number=N` (authoritative? active?
  the neighbouring problem numbers), which drives the shared header's navigation
  and its init/reset/eval/save/del action buttons.

- **Workspace control & edits** — all guarded by the workspace lock, returning
  HTTP 403 when the server is not authoritative over it (lock acquired or
  inherited; see :func:`solver.core.lock.acquire_workspace_lock`):
  `POST /<n>/cmd` runs a workspace command (`init`, `reset`, or `eval`);
  `POST /<n>/<file>` validates and saves an edited workspace file;
  `DELETE /<n>/<file>` removes a solution; `POST /progress` saves the progress file.
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
from typing import Any, Literal, TypedDict

from aiohttp import WSMsgType, web

from solver.config import config
from solver.core.evaluate import benchmark, evaluate
from solver.core.problems import Problem, problems
from solver.shell import console
from solver.utils.summary import summary
from solver.web.pty_bridge import PtySession


class _State(TypedDict):
    """Mutable per-server runtime state shared across requests.

    The aiohttp `Application` mapping is frozen once the server starts, so request
    handlers cannot reassign `app[key]`; live state instead lives in this single
    mutable value, stashed under :data:`_STATE` at setup and mutated in place.
    """
    #: Whether a PTY shell session is active (only one is allowed at a time).
    has_session: bool
    #: Last non-zero problem number queried via /flags, echoed back on the
    #: problem-less pages (summary / progress) so the header can still navigate.
    last_problem: int | None


#: Key under which the shared mutable state is stored on the Application.
_STATE: web.AppKey[_State] = web.AppKey('state', _State)

#: Top-level static page assets served verbatim from `config.static_file_dir`.
_STATIC_ASSETS: frozenset[str] = frozenset({
    'code.css', 'code.html', 'code.js', 'common.css', 'favicon.svg', 'header.css', 'header.html',
    'header.js', 'problem.css', 'problem.html', 'problem.js', 'problems.json', 'progress.css',
    'progress.js', 'solver.css', 'solver-theme.css', 'solver.html', 'solver.js', 'summary.css',
    'summary.html', 'summary.js',
})

#: mime type of a served problem file → highlight.js language for the code viewer.
_CODE_LANGUAGES: dict[str, str] = {
    'text/x-python': 'python',
    'text/x-csrc': 'c',
}


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


async def _serve_solver_page(request: web.Request) -> web.StreamResponse:
    """Serve the xterm.js terminal page (the default landing page at `/`)."""
    return web.FileResponse(config.static_file_dir / 'solver/solver.html')


async def _serve_summary_page(request: web.Request) -> web.StreamResponse:
    """Serve the solutions summary page (`/summary`)."""
    return web.FileResponse(config.static_file_dir / 'summary/summary.html')


async def _serve_progress_page(request: web.Request) -> web.StreamResponse:
    """Serve the progress file in an editable textarea (`GET /progress`).

    The file (`config.static_file_progress`) lives outside the workspace; its content
    is HTML-escaped into a textarea that POSTs back to `/progress` via the Save button.
    """
    path = config.static_file_progress
    content = path.read_text(encoding='utf-8') if path.is_file() else ''
    page = config.static_file_progress_editor.read_text().replace('{{CONTENT}}', html.escape(content))
    return _bytes_response(page.encode('utf-8'), 'text/html')


def _save_progress(content: bytes) -> tuple[int, str]:
    """Write edited content to the progress file; return (status, message) or None (→ 403).

    Guarded by the workspace lock (None → HTTP 403 when not authoritative). The file is
    outside the workspace, so no per-problem checks apply — the bytes are written verbatim.
    """
    config.static_file_progress.write_bytes(content)
    summary()
    return 200, f'saved {config.static_file_progress.name}'


async def _save_progress_page(request: web.Request) -> web.StreamResponse:
    """Save the edited progress file (`POST /progress`)."""
    body = await request.read()
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, _save_progress, body)
    return _text(*result)


async def _serve_vendor_asset(request: web.Request) -> web.StreamResponse:
    """Serve a vendored front-end asset under `static-content/vendor/`.

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


async def _pump_pty_to_ws(session: PtySession, ws: web.WebSocketResponse) -> None:
    """Stream PTY output to the WebSocket until the shell exits or the socket closes.

    `session.read` is a blocking `os.read` on the master fd, so it runs in the
    default executor; awaiting each send in turn keeps the byte stream strictly
    ordered. An empty read means the child shell has exited, which closes the socket.
    """
    loop = asyncio.get_running_loop()
    while True:
        data = await loop.run_in_executor(None, session.read)
        if not data or ws.closed:
            break
        await ws.send_bytes(data)
    if not ws.closed:
        await ws.close()


async def _ws_handler(request: web.Request, save: bool) -> web.WebSocketResponse:
    """Bridge a browser terminal to a fresh PTY-backed `solver` shell.

    Refuses a second concurrent connection (the single shared workspace must not
    have two live shells). Binary frames are forwarded to the PTY as keystrokes;
    a `resize` text frame propagates the browser geometry to the PTY.
    """
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    state = request.app[_STATE]
    if state['has_session']:
        await ws.send_str('\x1b[31ma solver session is already active in another tab\x1b[0m\r\n')
        await ws.close()
        return ws
    state['has_session'] = True

    session = PtySession(save=save)
    pump = asyncio.create_task(_pump_pty_to_ws(session, ws))
    try:
        async for msg in ws:
            if msg.type == WSMsgType.BINARY:
                session.write(msg.data)
            elif msg.type == WSMsgType.TEXT:
                if (size := _parse_resize(msg.data)) is not None:
                    session.resize(cols=size[0], rows=size[1])
            elif msg.type == WSMsgType.ERROR:
                break
    finally:
        pump.cancel()
        session.close()
        state['has_session'] = False
    return ws


# ---------------------------------------------------------------------------
# Viewer helpers (ported from the retired solver.utils.server)
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
    """Validate edited content and write it into the workspace; return (status, message).

    Guarded by the workspace lock: returns None (→ HTTP 403) when the server is not
    authoritative here. Otherwise status mirrors HTTP — 200 saved, 400 on a bad
    request or failed validation. JSON is parsed, Python is flake8-linted, and C is
    compiled before the file is accepted; on any validation failure the previous
    content is restored so a bad edit never lands.
    """
    if Path(filename).name != filename or Path(filename).suffix not in ('.py', '.c', '.json'):
        return 400, f'{filename} is not an editable workspace file'
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


def _lint_content(problem_number: int, filename: str, content: bytes) -> tuple[int, str]:
    """Lint edited content without saving it; return (status, JSON diagnostics).

    Runs the same validators as save — flake8 for Python, the runner-aware compile
    for C — against a throwaway temp copy, so the workspace file is never touched
    and a syntactically broken buffer is still diagnosable. Guarded by the workspace
    lock (None → HTTP 403), matching the editor's editable gating. The reply is
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
    """Delete a solution from the workspace; return (status, message) or None (→ 403)."""
    if Path(filename).name != filename or Path(filename).suffix not in ('.py', '.c'):
        return 400, f'{filename} is not a deletable workspace file'
    try:
        problem: Problem = Problem.from_number(problem_number)
    except ValueError:
        return 200, f'deleted {filename}'
    target: Path = problem.solution_dir.joinpath(filename)
    target.unlink(missing_ok=True)
    return 200, f'deleted {filename}'


def _run_cmd(problem_number: int,
             cmd: Literal['benchmark', 'eval'],
             lang: Literal['*', 'py', 'c'] | None = None,
             solution_index: int | None = None,
             ) -> tuple[int, str]:
    """Run a workspace command on *problem_number*; return (status, output) or None (→ 403).

    Guarded by the workspace lock (None → HTTP 403 when not authoritative). Each
    command maps onto the matching shell verb and its console output is captured as
    plain text for the caller to display:

    - `init`  — unstack the problem into the workspace, resetting a different active
      problem first (:func:`solver.core.workspace.init`); allowed whatever is active.
    - `reset` — stack any changes and clear the workspace; requires *problem_number*
      to be the active workspace.
    - `eval`  — evaluate solutions against the test cases; requires *problem_number*
      to be active. With neither *lang* nor *solution_index* it evaluates every
      solution (the problem page's button); the code page passes a specific
      (lang, index) to evaluate a single solution.

    Status mirrors HTTP: 200 when the command exits 0, 400 on a bad request or a
    non-zero command exit.
    """
    with console.capture() as capture:
        if cmd == 'benchmark':
            rcode = benchmark(lang=lang or '*', solution_index=solution_index)
        elif cmd == 'eval':
            rcode = evaluate(lang=lang or '*', solution_index=solution_index)
        else:
            return 400, f'unknown command {cmd}'  # type: ignore[unreachable]
    output = capture.get().strip()
    return (200 if rcode == 0 else 400), output


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


async def _problem_file(request: web.Request) -> web.StreamResponse:
    """Serve a single problem file for `/<n>/<filename>`.

    `solutions` is the synthesised solution listing; source files render through
    the code viewer on a browser navigation; JSON gets the viewer only when a human
    is navigating (problem.js fetches with Accept: application/json for raw bytes).
    """
    problem_number = int(request.match_info['problem_number'])
    filename = request.match_info['filename']
    if '..' in Path(filename).parts:  # filename may hold a subdir (resources/…); reject traversal
        raise web.HTTPNotFound()
    if problem_number < 1 or problem_number > problems.last_problem.number:
        raise web.HTTPNotFound()
    try:
        problem: Problem = Problem.from_number(problem_number)
    except ValueError:
        raise web.HTTPNotFound()
    if filename == 'solutions':
        files: list[str] = []
        for file in problem.solution_dir.glob(f'p{problem_number:04d}_s*.*'):
            if file.suffix == '.enc':
                file = file.with_suffix('')
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


#: Message returned (HTTP 403) when a write helper is refused for lack of the lock.
_READ_ONLY: str = 'workspace is read-only here'


def _text(code: int, message: str) -> web.Response:
    """A plain-text response with the given HTTP status."""
    return web.Response(status=code, text=message, content_type='text/plain', charset='utf-8')


async def _save_problem_file(request: web.Request) -> web.StreamResponse:
    """Save an edited workspace file (`POST /<n>/<filename>`)."""
    problem_number = int(request.match_info['problem_number'])
    filename = request.match_info['filename']
    body = await request.read()
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, functools.partial(_save_content, problem_number, filename, body))
    return _text(*result)


async def _delete_problem_file(request: web.Request) -> web.StreamResponse:
    """Delete a solution from the workspace (`DELETE /<n>/<filename>`)."""
    problem_number = int(request.match_info['problem_number'])
    filename = request.match_info['filename']
    result = _del_solution(problem_number, filename)
    return _text(*result)


async def _run_command(request: web.Request) -> web.StreamResponse:
    """Run a workspace command on the problem (`POST /<n>/cmd`).

    Body: `{"cmd": "init"|"reset"|"eval", "lang"?: "py"|"c", "solution_index"?: int}`
    — *lang* / *solution_index* are only meaningful for `eval` (omit them to evaluate
    every solution). Replies with JSON `{"output": <captured text>, "rcode": 0|1|null}`;
    the page renders the output. 400 for a malformed body, 403 when the server is not
    authoritative over the workspace.
    """
    problem_number: int = int(request.match_info['problem_number'])
    try:
        data = await request.json()
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise web.HTTPBadRequest()
    if not isinstance(data, dict):
        raise web.HTTPBadRequest()
    if (cmd := data.get('cmd')) not in ('init', 'reset', 'eval'):
        raise web.HTTPBadRequest()
    lang: Literal['py', 'c'] | None = data.get('lang')
    solution_index: int | None = data.get('solution_index')
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, _run_cmd, problem_number, cmd, lang, solution_index)
    code, output = result
    return web.json_response({'output': output, 'rcode': 0 if code == 200 else 1}, status=code)


async def _lint_problem_file(request: web.Request) -> web.StreamResponse:
    """Lint an edited (unsaved) workspace file (`POST /<n>/lint`).

    Body: `{"filename": "p0007_s0.py", "content": "<source>"}`. Replies with JSON
    `{"diagnostics": [...]}` the editor renders as inline squiggles; 403 when the
    server is not authoritative over the workspace, 400 for a malformed body.
    """
    problem_number = int(request.match_info['problem_number'])
    try:
        data = await request.json()
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise web.HTTPBadRequest()
    if not isinstance(data, dict) or not isinstance(data.get('filename'), str):
        raise web.HTTPBadRequest()
    content = str(data.get('content', '')).encode('utf-8')
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, _lint_content, problem_number, data['filename'], content)
    code, payload = result
    return web.Response(status=code, text=payload, content_type='application/json', charset='utf-8')


def build_app(save: bool) -> web.Application:
    """Construct the aiohttp application: terminal, WebSocket, and read-only viewer."""
    app = web.Application()
    state: _State = {'has_session': False, 'last_problem': None}
    app[_STATE] = state
    ws_handler = functools.partial(_ws_handler, save=save)
    app.add_routes([
        # Terminal + WebSocket. The terminal is the default landing page (`/`);
        web.get('/', _serve_solver_page),
        web.get('/ws', ws_handler),
        # Vendored assets: `/vendor/<asset>` for the JS/CSS/etc. that the editor needs.
        web.get(r'/vendor/{filename:.+}', _serve_vendor_asset),
        # Static pages: `/summary` → the solutions summary, `/<asset>` for the rest.
        web.get('/summary', _serve_summary_page),
        web.get('/progress', _serve_progress_page),
        web.get('/favicon.ico', _serve_favicon),
        web.get(r'/{asset:[A-Za-z0-9_.-]+\.(?:css|js|html|json|svg)}', _serve_static),
        # Problem viewer + edits (numeric problem number).
        web.get(r'/{problem_number:\d+}', _redirect_with_slash),
        web.get(r'/{problem_number:\d+}/', _problem_page),
        web.get(r'/{problem_number:\d+}/{filename:.+}', _problem_file),
        # Post actions: a workspace command (init / reset / eval), the progress save,
        # and an edited-file save. `/cmd` precedes the catch-all `/{filename}` so it
        # is matched as a command rather than a file named "cmd".
        web.post('/progress', _save_progress_page),
        web.post(r'/{problem_number:\d+}/cmd', _run_command),
        web.post(r'/{problem_number:\d+}/lint', _lint_problem_file),
        web.post(r'/{problem_number:\d+}/{filename}', _save_problem_file),
        # Delete a solution file from the workspace.
        web.delete(r'/{problem_number:\d+}/{filename}', _delete_problem_file),
    ])
    return app

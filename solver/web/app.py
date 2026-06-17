#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""aiohttp application: the SolverShell terminal, its PTY WebSocket, and the viewer.

`build_app` wires one localhost server with three concerns:

- **Terminal** — `GET /` serves the xterm.js page (the default landing page;
  `/solver` redirects to it) and `GET /ws` streams a
  single interactive `solver` shell on a pseudo-terminal (see
  :class:`solver.web.pty_bridge.PtySession`). Binary WS frames are raw terminal
  bytes both ways; a `{"resize": [cols, rows]}` text frame propagates geometry.
  Only one PTY session is allowed at a time — every session drives the shared
  `workspace/` and concurrent shells would race on it.

- **Read-only viewer** — the static summary/problem pages plus the problem files
  served through :func:`solver.core.stack.read_stack_file` (decrypting as needed,
  preferring the live workspace copy when a problem is active). Ported from the
  retired `solver.utils.server`; the old JSON control API (`/controls` +
  `flags`) is gone — the terminal does that work now.

- **Edits** — `POST /<n>/<file>` validates and saves an edited workspace file;
  `DELETE /<n>/<file>` removes a solution. Both require the server to be
  authoritative over the workspace (lock acquired or inherited; see
  :func:`solver.core.lock.acquire_workspace_lock`).
"""
from __future__ import annotations

__all__ = ['build_app']

import asyncio
import functools
import html
import json
import mimetypes
from pathlib import Path
from subprocess import run
from typing import Any

from aiohttp import WSMsgType, web

from solver.config import config
from solver.core import lock
from solver.core.evaluate import evaluate
from solver.core.problems import Problem
from solver.core.stack import read_stack_file, stack_base_dir
from solver.shell import console
from solver.web.pty_bridge import PtySession

#: Key under which the single-session flag is stored on the Application.
_HAS_SESSION: web.AppKey[list[bool]] = web.AppKey('has_session', list)

#: Top-level static page assets served verbatim from `config.static_file_dir`.
_STATIC_ASSETS: frozenset[str] = frozenset({
    'code.css', 'code.html', 'code.js', 'favicon.svg', 'problem.css', 'problem.html', 'problem.js',
    'problems.json', 'progress-editor.css', 'progress-editor.js', 'solver.css', 'solver.html',
    'solver.js', 'summary.css', 'summary.html', 'summary.js',
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
    return web.FileResponse(config.static_file_dir / name)


async def _serve_favicon(request: web.Request) -> web.StreamResponse:
    """Serve the SVG favicon for the default `/favicon.ico` browser request."""
    return web.FileResponse(config.static_file_dir / 'favicon.svg')


async def _serve_solver_page(request: web.Request) -> web.StreamResponse:
    """Serve the xterm.js terminal page (the default landing page at `/`)."""
    return web.FileResponse(config.static_file_dir / 'solver.html')


async def _serve_summary_page(request: web.Request) -> web.StreamResponse:
    """Serve the solutions summary page (`/summary`)."""
    return web.FileResponse(config.static_file_dir / 'summary.html')


async def _serve_progress_page(request: web.Request) -> web.StreamResponse:
    """Serve the progress file in an editable textarea (`GET /progress`).

    The file (`config.static_file_progress`) lives outside the workspace; its content
    is HTML-escaped into a textarea that POSTs back to `/progress` via the Save button.
    """
    path = config.static_file_progress
    content = path.read_text(encoding='utf-8') if path.is_file() else ''
    page = config.static_file_progress_editor.read_text().replace('{{CONTENT}}', html.escape(content))
    return _bytes_response(page.encode('utf-8'), 'text/html')


@lock.check_workspace_lock_generic
def _save_progress(content: bytes) -> tuple[int, str]:
    """Write edited content to the progress file; return (status, message) or None (→ 403).

    Guarded by the workspace lock (None → HTTP 403 when not authoritative). The file is
    outside the workspace, so no per-problem checks apply — the bytes are written verbatim.
    """
    config.static_file_progress.write_bytes(content)
    return 200, f'saved {config.static_file_progress.name}'


async def _save_progress_page(request: web.Request) -> web.StreamResponse:
    """Save the edited progress file (`POST /progress`)."""
    body = await request.read()
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, functools.partial(_save_progress, body))
    if result is None:  # check_workspace_lock_generic refused: not authoritative here
        return _text(403, _READ_ONLY)
    return _text(*result)


async def _redirect_to_root(request: web.Request) -> web.StreamResponse:
    """Redirect the old `/solver` URL to the new default `/`."""
    raise web.HTTPMovedPermanently('/')


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

    has_session = request.app[_HAS_SESSION]
    if has_session[0]:
        await ws.send_str('\x1b[31ma solver session is already active in another tab\x1b[0m\r\n')
        await ws.close()
        return ws
    has_session[0] = True

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
        has_session[0] = False
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
    template = (config.static_file_dir / 'code.html').read_bytes()
    page = (template.decode('utf-8')
            .replace('{{FILENAME}}', html.escape(filename))
            .replace('{{LANGUAGE}}', language)
            .replace('{{CODE}}', html.escape(content.decode('utf-8', errors='replace'))))
    return page.encode('utf-8')


def _read_problem_file(problem_number: int, filename: str) -> bytes:
    """Read a problem file, preferring the live workspace copy when active.

    While *problem_number* is the active workspace, its files are served from
    workspace/ so the viewer reflects unsaved edits and round-trips with the
    editor's save. Otherwise (and for any file absent from the workspace) the
    stacked copy is read, decrypting as needed. Returns (content, mtime).
    """
    if ((problem := Problem.from_workspace()) is not None and problem.number == problem_number
            and (workspace_file := config.workspace_dir / filename).is_file()):
        return workspace_file.read_bytes()
    content = read_stack_file(problem_number, filename)[0]
    return content


def _list_solutions(problem_number: int) -> bytes:
    """Return the JSON array of a problem's solution file names (workspace or stack)."""
    if (problem := Problem.from_workspace()) is not None and problem.number == problem_number:
        source_dir: Path = config.workspace_dir
    else:
        source_dir = stack_base_dir(problem_number)
    files: list[str] = []
    for file in source_dir.glob(f'p{problem_number:04d}_s*.*'):
        if file.suffix == '.enc':
            file = file.with_suffix('')
        files.append(f'{file.stem}_c' if file.suffix == '.c' else file.name)
    return json.dumps(sorted(files), indent=2).encode('utf-8')


def _workspace_flags(problem_number: int) -> bytes:
    """Report whether the editor may write to *problem_number* via this server.

    `authoritative` is True when the server holds the workspace lock (acquired
    standalone or inherited from a launching shell) and can therefore mutate it;
    `active` is True when *problem_number* is the problem currently in the
    workspace. The code.html editor enables Save/Eval/Delete only when both hold.
    """
    authoritative = lock.lock_state.acquired or lock.lock_state.inherited
    problem = Problem.from_workspace()
    active = problem is not None and problem.number == problem_number
    return json.dumps({'authoritative': authoritative, 'active': active}).encode('utf-8')


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


@lock.check_workspace_lock_generic
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
    if (problem := Problem.from_workspace()) is None or problem.number != problem_number:
        return 400, f'problem {problem_number} is not the active workspace'
    target: Path = config.workspace_dir / filename
    if not target.is_file():
        return 400, f'{filename} not in the workspace'
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


@lock.check_workspace_lock_generic
def _del_solution(problem_number: int, filename: str) -> tuple[int, str]:
    """Delete a solution from the workspace; return (status, message) or None (→ 403)."""
    if Path(filename).name != filename or Path(filename).suffix not in ('.py', '.c'):
        return 400, f'{filename} is not a deletable workspace file'
    if (problem := Problem.from_workspace()) is None or problem.number != problem_number:
        return 400, f'problem {problem_number} is not the active workspace'
    target: Path = config.workspace_dir / filename
    if not target.is_file():
        return 400, f'{filename} not in the workspace'
    target.unlink()
    return 200, f'deleted {filename}'


@lock.check_workspace_lock_generic
def _run_eval(problem_number: int, lang: str, solution_index: int) -> tuple[int, str]:
    """Evaluate a single solution against its test cases; return (status, output) or None (→ 403).

    `evaluate` reports through the shared console, captured here as plain text the
    editor renders in its output panel.
    """
    if (problem := Problem.from_workspace()) is None or problem.number != problem_number:
        return 400, f'problem {problem_number} is not the active workspace'
    with console.capture() as capture:
        rcode = evaluate(lang=lang, solution_index=solution_index)  # type: ignore[arg-type]
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
    return web.FileResponse(config.static_file_dir / 'problem.html')


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
    if filename == 'solutions':
        return _render_json(request, 'solutions', _list_solutions(problem_number))
    if filename == 'flags':
        return _render_json(request, 'flags', _workspace_flags(problem_number))
    try:
        content: bytes = _read_problem_file(problem_number, filename)
    except (FileNotFoundError, KeyError, ValueError):
        raise web.HTTPNotFound()
    mime, _ = mimetypes.guess_type(filename)
    if (language := _CODE_LANGUAGES.get(mime or '')) is not None:
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
    if result is None:  # check_workspace_lock_generic refused: not authoritative here
        return _text(403, _READ_ONLY)
    return _text(*result)


async def _delete_problem_file(request: web.Request) -> web.StreamResponse:
    """Delete a solution from the workspace (`DELETE /<n>/<filename>`)."""
    problem_number = int(request.match_info['problem_number'])
    filename = request.match_info['filename']
    result = _del_solution(problem_number, filename)
    if result is None:
        return _text(403, _READ_ONLY)
    return _text(*result)


async def _eval_solution(request: web.Request) -> web.StreamResponse:
    """Evaluate one solution against its test cases (`POST /<n>/eval`).

    Body: `{"lang": "py"|"c", "solution_index": int}`. Replies with JSON
    `{"output": <captured text>, "rcode": <int>}`; the editor shows the output.
    """
    problem_number = int(request.match_info['problem_number'])
    try:
        data = await request.json()
    except (json.JSONDecodeError, UnicodeDecodeError):
        data = {}
    lang = data.get('lang') if isinstance(data, dict) else None
    solution_index = data.get('solution_index') if isinstance(data, dict) else None
    if lang not in ('py', 'c') or type(solution_index) is not int:
        return web.json_response({'output': 'eval needs lang (py|c) and an integer solution_index',
                                  'rcode': None}, status=400)
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, functools.partial(_run_eval, problem_number, lang, solution_index))
    if result is None:
        return web.json_response({'output': _READ_ONLY, 'rcode': None}, status=403)
    code, output = result
    return web.json_response({'output': output, 'rcode': 0 if code == 200 else 1}, status=code)


def build_app(save: bool) -> web.Application:
    """Construct the aiohttp application: terminal, WebSocket, and read-only viewer."""
    app = web.Application()
    app[_HAS_SESSION] = [False]
    ws_handler = functools.partial(_ws_handler, save=save)
    app.add_routes([
        # Terminal + WebSocket. The terminal is the default landing page (`/`);
        web.get('/', _serve_solver_page),
        web.get('/ws', ws_handler),
        web.get(r'/vendor/{filename:.+}', _serve_vendor_asset),
        # Static pages: `/summary` → the solutions summary, `/<asset>` for the rest.
        web.get('/summary', _serve_summary_page),
        web.get('/progress', _serve_progress_page),
        web.post('/progress', _save_progress_page),
        web.get('/favicon.ico', _serve_favicon),
        web.get(r'/{asset:[A-Za-z0-9_.-]+\.(?:css|js|html|json|svg)}', _serve_static),
        # Problem viewer + edits (numeric problem number).
        web.get(r'/{problem_number:\d+}', _redirect_with_slash),
        web.get(r'/{problem_number:\d+}/', _problem_page),
        web.get(r'/{problem_number:\d+}/{filename:.+}', _problem_file),
        web.post(r'/{problem_number:\d+}/eval', _eval_solution),
        web.post(r'/{problem_number:\d+}/{filename}', _save_problem_file),
        web.delete(r'/{problem_number:\d+}/{filename}', _delete_problem_file),
    ])
    return app

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

- **Edits** — `POST /<n>/cmd` evaluates the problem's solutions; `POST /<n>/<file>`
  validates and saves an edited solution file; `DELETE /<n>/<file>` removes a
  solution; `POST /progress` saves the progress file.
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
from typing import Any, Literal

from aiohttp import WSCloseCode, WSMsgType, web

from solver.config import config
from solver.core.evaluate import benchmark, evaluate
from solver.core.problems import Problem, problems
from solver.shell import console
from solver.shell.variables import variables
from solver.utils.identity import slugify
from solver.utils.summary import summary
from solver.web.auth.routes import USER_EMAIL, WS_CONNECTIONS, auth_middleware, setup_auth
from solver.web.pty_manager import PTY_MANAGER, setup_pty_manager

#: Top-level static page assets served verbatim from `config.static_file_dir`.
_STATIC_ASSETS: frozenset[str] = frozenset({
    'code.css', 'code.html', 'code.js', 'common.css', 'favicon.svg', 'header.css', 'header.html',
    'header.js', 'problem.css', 'problem.html', 'problem.js', 'problems.json', 'progress.css',
    'progress.js', 'solver.css', 'solver-theme.css', 'solver.html', 'solver.js', 'summary.css',
    'summary.html', 'summary.js',
    'login.css', 'login.js', 'srp-client.js', 'register.css', 'register.js',
    'password.css', 'password.js',
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
    """Serve the progress file in an editable textarea (`GET /progress`).

    The file (`config.static_file_progress`) lives outside the solution tree; its
    content is HTML-escaped into a textarea that POSTs back to `/progress` via the
    Save button.
    """
    path = config.static_file_progress
    content = path.read_text(encoding='utf-8') if path.is_file() else ''
    page = config.static_file_progress_editor.read_text().replace('{{CONTENT}}', html.escape(content))
    return _bytes_response(page.encode('utf-8'), 'text/html')


def _save_progress(content: bytes) -> tuple[int, str]:
    """Write edited content to the progress file; return (status, message).

    The file is outside the solution tree, so no per-problem checks apply — the
    bytes are written verbatim (status mirrors HTTP: 200 saved).
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

    email: str = request[USER_EMAIL]   # set by auth_middleware (the /ws route is gated)
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
        pty.detach(ws)   # the shell keeps running; only this socket goes away
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
    if Path(filename).name != filename or Path(filename).suffix not in ('.py', '.c', '.json'):
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


def _run_cmd(problem_number: int,
             cmd: Literal['benchmark', 'eval'],
             lang: Literal['*', 'py', 'c'] | None = None,
             solution_index: int | None = None,
             ) -> tuple[int, str]:
    """Run a command on *problem_number*; return (status, output).

    Each command maps onto the matching shell verb and its console output is
    captured as plain text for the caller to display:

    - `eval`      — evaluate solutions against the test cases. With neither *lang*
      nor *solution_index* it evaluates every solution (the problem page's button);
      the code page passes a specific (lang, index) to evaluate a single solution.
    - `benchmark` — time the problem's solutions (same *lang* / *solution_index*
      selection as `eval`).

    Status mirrors HTTP: 200 when the command exits 0, 400 on a bad request or a
    non-zero command exit.
    """
    problem: Problem = Problem.from_number(problem_number)
    with console.capture() as capture:
        if cmd == 'benchmark':
            rcode = benchmark(problem, lang=lang or '*', solution_index=solution_index)
        elif cmd == 'eval':
            rcode = evaluate(problem, lang=lang or '*', solution_index=solution_index)
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


def _text(code: int, message: str) -> web.Response:
    """A plain-text response with the given HTTP status."""
    return web.Response(status=code, text=message, content_type='text/plain', charset='utf-8')


async def _save_problem_file(request: web.Request) -> web.StreamResponse:
    """Save an edited solution file (`POST /<n>/<filename>`)."""
    problem_number = int(request.match_info['problem_number'])
    filename = request.match_info['filename']
    body = await request.read()
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, functools.partial(_save_content, problem_number, filename, body))
    return _text(*result)


async def _delete_problem_file(request: web.Request) -> web.StreamResponse:
    """Delete a solution (`DELETE /<n>/<filename>`)."""
    problem_number = int(request.match_info['problem_number'])
    filename = request.match_info['filename']
    result = _del_solution(problem_number, filename)
    return _text(*result)


async def _run_command(request: web.Request) -> web.StreamResponse:
    """Run a command on the problem (`POST /<n>/cmd`).

    Body: `{"cmd": "eval"|"benchmark", "lang"?: "py"|"c", "solution_index"?: int}`
    — *lang* / *solution_index* select a single solution (omit them to run every
    solution). Replies with JSON `{"output": <captured text>, "rcode": 0|1|null}`;
    the page renders the output. 400 for a malformed body.
    """
    problem_number: int = int(request.match_info['problem_number'])
    try:
        data = await request.json()
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise web.HTTPBadRequest()
    if not isinstance(data, dict):
        raise web.HTTPBadRequest()
    if (cmd := data.get('cmd')) not in ('eval', 'benchmark'):
        raise web.HTTPBadRequest()
    lang: Literal['py', 'c'] | None = data.get('lang')
    solution_index: int | None = data.get('solution_index')
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, _run_cmd, problem_number, cmd, lang, solution_index)
    code, output = result
    return web.json_response({'output': output, 'rcode': 0 if code == 200 else 1}, status=code)


async def _lint_problem_file(request: web.Request) -> web.StreamResponse:
    """Lint an edited (unsaved) solution file (`POST /<n>/lint`).

    Body: `{"filename": "p0007_s0.py", "content": "<source>"}`. Replies with JSON
    `{"diagnostics": [...]}` the editor renders as inline squiggles; 400 for a
    malformed body.
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
    app.add_routes([
        # Terminal + WebSocket. The terminal is the default landing page (`/`);
        web.get('/', _serve_solver_page),
        web.get('/ws', ws_handler),
        # Vendored assets: `/vendor/<asset>` for the JS/CSS/etc. that the editor needs.
        web.get(r'/vendor/{filename:.+}', _serve_vendor_asset),
        # Static pages: `/summary` → the solutions summary, `/<asset>` for the rest.
        web.get('/summary', _serve_summary_page),
        web.get('/progress', _serve_progress_page),
        web.get('/active-problem', _serve_active_problem),
        web.get('/favicon.ico', _serve_favicon),
        web.get(r'/{asset:[A-Za-z0-9_.-]+\.(?:css|js|html|json|svg)}', _serve_static),
        # Problem viewer + edits (numeric problem number).
        web.get(r'/{problem_number:\d+}', _redirect_with_slash),
        web.get(r'/{problem_number:\d+}/', _problem_page),
        web.get(r'/{problem_number:\d+}/{filename:.+}', _problem_file),
        # Post actions: a command (eval / benchmark), the progress save, and an
        # edited-file save. `/cmd` precedes the catch-all `/{filename}` so it
        # is matched as a command rather than a file named "cmd".
        web.post('/progress', _save_progress_page),
        web.post(r'/{problem_number:\d+}/cmd', _run_command),
        web.post(r'/{problem_number:\d+}/lint', _lint_problem_file),
        web.post(r'/{problem_number:\d+}/{filename}', _save_problem_file),
        # Delete a solution file.
        web.delete(r'/{problem_number:\d+}/{filename}', _delete_problem_file),
    ])
    return app

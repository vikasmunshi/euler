#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Utilities for visualizing solutions. 1. Web server, 2. Browser."""
from __future__ import annotations

import http.server
import mimetypes
import socketserver
import threading
import urllib.parse
from email.utils import formatdate
from functools import lru_cache
from subprocess import CalledProcessError, run
from typing import Literal

from solver.config import config
from solver.core.problems import Problem
from solver.core.stack import read_stack_file
from solver.shell import console, register

# ---------------------------------------------------------------------------
# Web server
# ---------------------------------------------------------------------------

_server: _ReusingTCPServer | None = None


class _ReusingTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


@lru_cache(maxsize=None)
def _read_static_asset(filename: str) -> tuple[bytes, float]:
    """Read a static solution asset from disk; result is cached until reload_static_cache()."""
    path = config.solutions_dir / filename
    return path.read_bytes(), path.stat().st_mtime


def reload_static_cache() -> None:
    """Clear the in-memory cache of static solution assets.

    Call after writing to any file served as a top-level static asset
    (e.g. problems.json updates from mark_solved) so subsequent requests
    re-read from disk.
    """
    _read_static_asset.cache_clear()


class _SolutionHandler(http.server.BaseHTTPRequestHandler):
    """Serve solution files: page assets from disk, problem files via read_stack_file.

    URL layout mirrors the on-disk structure:
      /                                  → solutions/index.html (disk read)
      /index.html, /index.css, /index.js, /problems.json → solutions/<name> (disk read)
      /d1/d2/d3/d4/<filename>            → read_stack_file(problem_number, filename)
      /d1/d2/d3/d4/resources/<file>      → read_stack_file(problem_number, resources/<file>)
    """

    _static_assets: dict[str, str] = {
        '/index.html': 'index.html',
        '/index.css': 'index.css',
        '/index.js': 'index.js',
        '/problem.css': 'problem.css',
        '/problem.js': 'problem.js',
        '/problems.json': 'problems.json',
    }

    def do_GET(self) -> None:
        path = urllib.parse.urlparse(self.path).path

        if path == '/':
            path = '/index.html'
        if path in self._static_assets:
            filename = self._static_assets[path]
            try:
                content, mtime = _read_static_asset(filename)
            except FileNotFoundError:
                self._not_found(f'{filename} does not exist')
                return
            mime, _ = mimetypes.guess_type(filename)
            self._respond(200, mime or 'application/octet-stream', content, last_modified=mtime)
            return

        # Expect /d1/d2/d3/d4/<filename...> — 4 single-digit path segments then filename
        parts = path.lstrip('/').split('/')
        if len(parts) < 5 or not all(p.isdigit() and len(p) == 1 for p in parts[:4]):
            self._not_found(f'{path!r} is not valid')
            return
        try:
            problem_number = int(''.join(parts[:4]))
            filename = '/'.join(parts[4:])
            content, _, mtime = read_stack_file(problem_number, filename)
        except (FileNotFoundError, KeyError, ValueError) as e:
            self._not_found(f'no access to {path}; {e!r}')
            return
        else:
            mime, _ = mimetypes.guess_type(filename)
            self._respond(200, mime or 'application/octet-stream', content, last_modified=mtime)

    def _respond(self, code: int, content_type: str, body: bytes, last_modified: float | None = None) -> None:
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        if last_modified is not None:
            self.send_header('Last-Modified', formatdate(last_modified, usegmt=True))
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass  # quietly ignore

    def _not_found(self, message: str) -> None:
        body = f'<h3>404 Not Found</h3><p><em>{message}</em></p>'.encode()
        self._respond(404, 'text/html; charset=utf-8', body)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        pass

    def log_error(self, format: str, *args: object) -> None:  # noqa: A002
        pass

    def handle(self) -> None:
        try:
            super().handle()
        except Exception:  # noqa: BLE001
            pass  # quietly ignore


@register(name='server',
          help='Start, stop, or check the local solution web server.',
          usage='server [start|stop|status=status]')
def manage_server(action: Literal['start', 'stop', 'status'] = 'status') -> Literal['ok', 'nok']:
    """Manage the lightweight HTTP server that serves solution files.

    Arguments:
        action: "start" launches the server, "stop" shuts it down,
                "status" (default) reports whether it is running.
    """
    global _server

    if action == 'start':
        if _server is not None:
            console.print(f'[muted]server already running on http://localhost:{config.server_port}[/muted]')
            return 'ok'
        try:
            _server = _ReusingTCPServer(('localhost', config.server_port), _SolutionHandler)
        except OSError as exc:
            console.print(f'[error]error:[/error] [muted]cannot start server: {exc}[/muted]')
            return 'nok'
        threading.Thread(target=_server.serve_forever, daemon=True).start()
        console.print(f'[accent]server started[/accent] [muted]- http://localhost:{config.server_port}[/muted]')
        return 'ok'

    elif action == 'stop':
        if _server is None:
            console.print('[muted]server is not running[/muted]')
            return 'ok'
        _server.shutdown()
        _server = None
        console.print('[muted]server stopped[/muted]')
        return 'ok'

    else:  # status
        if _server is None:
            console.print('[muted]server is not running[/muted]')
            return 'ok'
        else:
            console.print(f'[accent]running[/accent] [muted]- http://localhost:{config.server_port}[/muted]')
            return 'ok'


# ---------------------------------------------------------------------------
# Browser
# ---------------------------------------------------------------------------

@lru_cache(maxsize=None)
def browser_is_available() -> bool:
    """Return "True" if the "browser" executable is present on "PATH".

    The result is cached after the first call.
    """
    try:
        run('command browser -h 1>/dev/null 2>&1', shell=True, check=True)
        return True
    except CalledProcessError:
        return False


@register(name='browser',
          help='Open problem documentation in a browser.',
          usage='browser [problem_number=0]',
          aliases=('open', 'show', 'view'))
def show_in_browser(problem_number: int = 0) -> None:
    """Open a problem's "problem.html" in the system browser.

    When *problem_number* is "0" (default), opens the problem currently in the workspace.

    Prints an error and returns early if:
    - the "browser" command is not available, or
    - the resolved "problem.html" file does not exist.

    Arguments:
        problem_number: Problem to open; "0" means the current workspace.
    """
    if not browser_is_available():
        console.print('[error]error:[/error] [muted]"browser" command not available; '
                      'use [accent]solver install chrome[/accent] to install Chrome[/muted]')
        return
    if _server is None:
        manage_server('start')
    if problem_number == 0 and (problem := Problem.from_workspace()) is not None:
        problem_number = problem.number
    url: str = (f'http://localhost:{config.server_port}/'
                f'{'index.html' if problem_number == 0 else ('/'.join(f'{problem_number:04d}') + '/problem.html')}')
    run(f'browser open {url}', shell=True)


__all__ = ('manage_server', 'reload_static_cache', 'show_in_browser')

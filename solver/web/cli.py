#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""`solver-web`: lifecycle for the PTY-backed SolverShell web front end.

The server runs as a detached child process so it keeps serving after the shell
that launched it exits; a PID file is the cross-process source of truth, so any
later shell (or a plain `solver-web stop`) can query or stop it.

The detached child wraps its entire runtime in a single `acquire_workspace_lock()`
context (see :mod:`solver.core.lock`). That covers every launch case with the
existing semantics: standalone it *acquires* the flock; launched from a running
shell it *inherits* it. Either way `config.lock_env_var` is set for the server's
lifetime, so every PTY child it forks (`python -m solver`) re-enters the lock and
**inherits** rather than fighting for it — there is never a flock conflict between
the server and its shells.
"""
from __future__ import annotations

__all__ = ['main', 'running_pid', 'ensure_running']

import argparse
import atexit
import os
import signal
import sys
import time
from subprocess import DEVNULL, Popen, run
from typing import Literal

from aiohttp import web

from solver.config import ExitCodes, config
from solver.core.lock import acquire_workspace_lock
from solver.shell import console
from solver.web.app import build_app


def running_pid(pid: int | None = None) -> int | None:
    """Return the PID of the running web server, or None if it is not running.

    The PID file survives shell exit, so any shell can query or stop a server
    started by another. A stale file (PID no longer alive) is treated
    as "not running".
    """
    try:
        pid = pid or int(config.server_pid_file.read_text().strip())
    except (FileNotFoundError, ValueError):
        return None
    try:
        os.kill(pid, 0)  # signal 0: liveness probe, does not actually signal
    except OSError:
        return None
    return pid


def _serve_forever(save: bool) -> None:  # pragma: no cover — runs in the detached child process
    """Hold the workspace lock and serve until terminated; the detached child entry point.

    The PID file is written only after the lock context is entered (so the env var
    is set for PTY children) and removed on exit. `web.run_app` installs its own
    SIGTERM/SIGINT handling and returns on signal, unwinding the lock cleanly.
    """
    console.width = config.screen_width  # stable width for captured command output (no tty here)
    with acquire_workspace_lock():
        config.server_pid_file.write_text(str(os.getpid()))
        atexit.register(config.server_pid_file.unlink, missing_ok=True)
        web.run_app(build_app(save=save), host='127.0.0.1', port=config.server_port, print=None)


def _start(save: bool = False) -> int:
    """Launch the detached server child; no-op if one is already running."""
    if (pid := running_pid()) is not None:
        console.print(f'[muted]web server already running on http://localhost:{config.server_port} (pid {pid})[/muted]')
        return ExitCodes.EXIT_OK
    argv = [sys.executable, '-m', 'solver.web.cli'] + (['--save'] if save else [])
    proc = Popen(argv, cwd=config.root_dir, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL,
                 start_new_session=True)
    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            console.print('[error]error:[/error] '
                          f'[muted]cannot start web server (port {config.server_port} in use?)[/muted]')
            return ExitCodes.EXIT_ERROR
        if (pid := running_pid()) is not None:
            console.print(f'[accent]web server started[/accent] '
                          f'[muted]- http://localhost:{config.server_port} (pid {pid})[/muted]')
            run(f'browser open http://localhost:{config.server_port} --no-refresh', shell=True)
            return ExitCodes.EXIT_OK
        time.sleep(0.05)
    console.print('[error]error:[/error] [muted]web server did not come up in time[/muted]')
    return ExitCodes.EXIT_ERROR


def _stop() -> int:
    """Terminate the running server, if any."""
    if (pid := running_pid()) is None:
        console.print('[muted]web server is not running[/muted]')
        return ExitCodes.EXIT_OK
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError as exc:
        console.print(f'[error]error:[/error] [muted]cannot stop web server: {exc}[/muted]')
        return ExitCodes.EXIT_ERROR
    while running_pid(pid=pid) is not None:
        time.sleep(0.1)
    console.print(f'[muted]web server stopped (pid {pid})[/muted]')
    return ExitCodes.EXIT_OK


def _status() -> int:
    """Report whether the server is running."""
    if (pid := running_pid()) is None:
        console.print('[muted]web server is not running[/muted]')
    else:
        console.print(f'[accent]running[/accent] [muted]- http://localhost:{config.server_port} (pid {pid})[/muted]')
    return ExitCodes.EXIT_OK


def ensure_running() -> int | None:
    """Start the server if it is not already up; return its PID (None on failure).

    Convenience for callers that want the server available (e.g. `show`) without
    caring whether it was already running.
    """
    if running_pid() is None:
        _start()
    return running_pid()


def main() -> int:
    """
    Parses command-line arguments and executes the specified application action.

    This function serves as the entry point for the command-line interface of the
    application. It processes user-provided arguments, determining the action to be
    taken, such as starting, stopping, restarting, or checking the status of the
    application.

    Returns
    -------
    int
        An integer status code indicating the result of the executed action.

    Raises
    ------
    SystemExit
        If invalid arguments are passed to the program or subcommands.
    """
    parser = argparse.ArgumentParser(prog='solver-web', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {config.version}')
    parser.add_argument('action', nargs='?', choices=('start', 'stop', 'status', 'restart'), default='status')
    parser.add_argument('-s', '--save', action='store_true', help=f'tee console output to {config.session_file.name}')

    args = parser.parse_args()
    action: Literal['start', 'stop', 'status', 'restart'] = args.action

    if action == 'start':
        return _start(args.save)
    if action == 'stop':
        return _stop()
    if action == 'restart':
        if (rcode := _stop()) != ExitCodes.EXIT_OK:
            return rcode
        return _start(args.save)
    return _status()


if __name__ == '__main__':  # pragma: no cover — detached server child process
    _serve_forever(save='--save' in sys.argv[1:])

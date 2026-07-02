#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""`solver-web`: lifecycle for the PTY-backed SolverShell web front end.

The server runs as a detached child process so it keeps serving after the shell
that launched it exits. The detached child holds an exclusive `fcntl.flock` on a
dedicated lock file for its whole lifetime (see :func:`hold_instance_lock`); that
flock is the cross-process source of truth for "is a server running", so any later
shell (or a plain `solver-web stop`) can probe or stop it. Because the OS drops
the lock when the process exits or crashes, there is never stale state to clean up
and a recycled PID can never produce a false positive. The PID is recorded as the
lock file's content purely so `stop`/`status` can report and signal it.

Every PTY child the server forks (`python -m solver`) is a plain `solver` shell
operating on the shared solution tree; the instance flock above is the only
cross-process lock the server holds.
"""
from __future__ import annotations

__all__ = ['main', 'running_pid', 'ensure_running']

import argparse
import fcntl
import os
import signal
import sys
import time
from pathlib import Path
from subprocess import DEVNULL, Popen, run
from typing import IO
from typing import Literal

from aiohttp import web

from solver.config import ExitCodes, config
from solver.shell import console
from solver.web.app import build_app

# Open file objects for instance locks held by this process, keyed by lock-file path. Kept alive for
# the process's lifetime: an `fcntl.flock` is tied to the open file description, so letting the object
# be garbage-collected (and its fd closed) would silently release the lock. `release_instance_lock`
# drops an entry here to release a lock before the process exits.
_instance_lock_fds: dict[Path, IO[str]] = {}


def hold_instance_lock(path: Path) -> bool:
    """Take an exclusive, process-lifetime flock on `path`, recording this process's PID in it.

    Used as a single-instance guard for a long-running process (e.g. the web server): the OS
    releases the lock automatically when the process exits or crashes, so no stale state is ever
    left behind. The PID is written as the file's content purely so that other processes can
    report it / signal it; the flock itself is the source of truth for liveness.

    Reentrant within this process: if we already hold the lock on `path` the call is a no-op that
    returns True (an flock from a second fd of the same file conflicts even with our own existing
    one, so a fresh acquire would otherwise spuriously fail).

    Returns True if the lock is held by this process afterwards, or False if another live process
    already holds it.
    """
    if path in _instance_lock_fds:
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    # Open without truncation so an existing holder's PID survives a failed acquire attempt.
    fd = path.open('a+')
    try:
        fcntl.flock(fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        fd.close()
        return False
    fd.seek(0)
    fd.truncate()
    fd.write(str(os.getpid()))
    fd.flush()
    _instance_lock_fds[path] = fd  # intentionally kept open for the process's lifetime
    return True


def release_instance_lock(path: Path) -> bool:
    """Release an instance flock previously taken via `hold_instance_lock` on `path`.

    Releases the `fcntl.flock`, closes the held fd, and removes the now-stale lock file. (A leftover
    file would be harmless — `probe_instance_lock` treats the flock as the source of truth — but it is
    cleaner to drop it.) Returns True if this process held the lock, or False if it did not.
    """
    fd = _instance_lock_fds.pop(path, None)
    if fd is None:
        return False
    fcntl.flock(fd.fileno(), fcntl.LOCK_UN)
    fd.close()
    path.unlink(missing_ok=True)
    return True


def probe_instance_lock(path: Path) -> int | None:
    """Return the PID of the process holding an instance flock on `path`, or None if it is free.

    Liveness is probed by attempting the lock non-blockingly from a fresh fd: if it can be
    acquired the holder is gone (we release at once and report None); if it is blocked a live
    process holds it, and we read its PID from the file's content for reporting. Because the
    truth is the flock, a stale file from a crashed process never produces a false positive.
    """
    try:
        fd = path.open('a+')
    except OSError:
        return None
    try:
        try:
            fcntl.flock(fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:  # held by a live process → running
            fd.seek(0)
            holder = fd.read().strip()
            return int(holder) if holder.isdigit() else None
        else:  # acquired → no live holder
            fcntl.flock(fd.fileno(), fcntl.LOCK_UN)
            return None
    finally:
        fd.close()


def running_pid() -> int | None:
    """Return the PID of the running web server, or None if it is not running.

    Probes the server's instance flock (held by the detached child for its whole
    lifetime), so any shell can query or stop a server started by another. The OS
    releases the flock on exit or crash, so a stale lock file is never mistaken
    for a live server.
    """
    return probe_instance_lock(config.server_lock_file)


def _serve_forever(save: bool) -> None:  # pragma: no cover — runs in the detached child process
    """Serve until terminated; the detached child entry point.

    Takes the instance flock; if it cannot be taken another server already owns it
    and we bail. `web.run_app` installs its own SIGTERM/SIGINT handling and returns
    on signal; the OS drops the instance flock as the process exits.
    """
    console.width = config.screen_width  # stable width for captured command output (no tty here)
    if not hold_instance_lock(config.server_lock_file):
        return  # lost the race: another server is already running
    web.run_app(build_app(save=save), host='127.0.0.1', port=config.server_port, print=None)


def _start(save: bool = False) -> int:
    """Launch the detached server child; no-op if one is already running."""
    if (pid := running_pid()) is not None:
        console.print(f'[muted]web server already running on {config.base_url} (pid {pid})[/muted]')
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
                          f'[muted]- {config.base_url} (pid {pid})[/muted]')
            run(f'browser open {config.base_url} --no-refresh', shell=True)
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
    while running_pid() is not None:
        time.sleep(0.1)
    console.print(f'[muted]web server stopped (pid {pid})[/muted]')
    return ExitCodes.EXIT_OK


def _status() -> int:
    """Report whether the server is running."""
    if (pid := running_pid()) is None:
        console.print('[muted]web server is not running[/muted]')
    else:
        console.print(f'[accent]running[/accent] [muted]- {config.base_url} (pid {pid})[/muted]')
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

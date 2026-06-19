#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Utilities for workspace locking using file-based locks."""
from __future__ import annotations

__all__ = ['acquire_workspace_lock', 'check_workspace_lock_generic', 'check_workspace_lock_command', 'lock_state',
           'hold_instance_lock', 'release_instance_lock', 'probe_instance_lock', 'descendant_pids',
           'proc_is_solver']

import contextlib
import fcntl
import functools
import os
from pathlib import Path
from typing import Callable, Generator, IO, NamedTuple

from solver.config import ExitCodes, config


class LockState(NamedTuple):
    acquired: bool
    inherited: bool
    pid_of_holder: int | None

    @property
    def held_by(self) -> str:
        return f' (held by PID {self.pid_of_holder})' if self.pid_of_holder else ''


_RELEASED: LockState = LockState(acquired=False, inherited=False, pid_of_holder=None)
_lock_state: LockState = _RELEASED


def lock_state() -> LockState:
    return _lock_state


def _workspace_lock_file() -> Path:
    """Return the workspace lock file — a sibling dotfile of the workspace directory."""
    ws = config.workspace_dir
    return ws.with_suffix('.lock') if ws.name.startswith('.') else ws.parent / f'.{ws.name}.lock'


def _read_ppid(pid: int) -> int:
    """Return the parent PID of `pid` from /proc, or 0 if it cannot be determined."""
    try:
        with open(f'/proc/{pid}/status') as status:
            for line in status:
                if line.startswith('PPid:'):
                    return int(line.split()[1])
    except (OSError, ValueError):
        pass
    return 0


def _self_and_ancestor_pids(max_depth: int = 16) -> frozenset[int]:
    """Return the PIDs of this process, its parent, and grandparents up to `max_depth` levels."""
    pids: set[int] = {os.getpid(), os.getppid()}
    pid: int = os.getpid()
    for _ in range(max_depth):
        pid = _read_ppid(pid)
        if pid <= 1:
            break
        pids.add(pid)
    return frozenset(pids)


def descendant_pids(root: int, max_procs: int = 65536) -> frozenset[int]:
    """Return the PIDs of every live descendant of `root` (the subtree below it, root excluded).

    Scans `/proc` once to build a parent → children map from each process's `PPid`, then walks
    down from `root`. Used to fan a workspace-change nudge out from the lock owner to every shell
    it spawned: the owner is an ancestor of all those shells (the web server's PTY children are
    forked under it and stay in its session), so the subtree below the owner is exactly the set of
    sibling shells to re-sync.
    """
    children: dict[int, list[int]] = {}
    try:
        entries = os.listdir('/proc')
    except OSError:
        return frozenset()
    for entry in entries[:max_procs]:
        if not entry.isdigit():
            continue
        ppid = _read_ppid(int(entry))
        if ppid:
            children.setdefault(ppid, []).append(int(entry))
    seen: set[int] = set()
    stack: list[int] = list(children.get(root, []))
    while stack:
        pid = stack.pop()
        if pid in seen:
            continue
        seen.add(pid)
        stack.extend(children.get(pid, []))
    return frozenset(seen)


def proc_is_solver(pid: int) -> bool:
    """Return whether `pid`'s command line is a `solver` shell (console script or `python -m solver`).

    Used to confine the workspace-change nudge to processes that actually run our code — and so have
    the SIGUSR1 handler installed (`solver.shell.variables`). Any other descendant (e.g. a `claude`
    child launched by `claude-skill`, or its `sh -c` wrapper) has SIGUSR1 at its default disposition,
    where the nudge would terminate it; filtering on this keeps the relay to sibling shells only.
    """
    try:
        with open(f'/proc/{pid}/cmdline', 'rb') as cmdline:
            argv = [part.decode('utf-8', 'replace') for part in cmdline.read().split(b'\0') if part]
    except OSError:
        return False
    if not argv:
        return False
    if os.path.basename(argv[0]) == 'solver':  # console-script entry point
        return True
    return argv[argv.index('-m') + 1: argv.index('-m') + 2] == ['solver'] if '-m' in argv else False


def _lock_held() -> bool:
    """
    Return True if the workspace lock is held by this process or an inherited ancestor.

    The PID of the process that acquired the flock is published in the `config.lock_env_var`
    environment variable, which child processes inherit. Since environment variables only flow
    from a parent to its children, a value present here was set by this process or one of its
    ancestors; we confirm by matching it against our own process tree.
    """
    holder: str = os.environ.get(config.lock_env_var, '')
    return holder.isdigit() and int(holder) in _self_and_ancestor_pids()


@contextlib.contextmanager
def acquire_workspace_lock() -> Generator[LockState, None, None]:
    """
    Acquire an exclusive lock on the workspace directory for the duration of the context.

    Uses OS-level file locking (fcntl.flock) so the lock is released automatically if the
    process exits or crashes — stale locks are never left behind. The acquiring PID is exported
    via `config.lock_env_var` so that child processes (and reentrant calls within this process)
    inherit the lock and skip re-acquisition rather than deadlocking against their own ancestor.

    Yields a `LockState` describing the outcome:
        - inherited: the lock is already held by this process or an ancestor (flock untouched).
        - acquired:  the flock was newly taken by this call.
        - neither:   the workspace is already locked by an unrelated process.
    """
    global _lock_state
    # Reentrant call: already inside an active context in this process; reuse it untouched.
    if _lock_state.acquired or _lock_state.inherited:
        yield _lock_state
        return
    # Inherited: an ancestor already holds the flock (detected via the inherited env var).
    if _lock_held():
        _lock_state = LockState(acquired=False, inherited=True, pid_of_holder=int(os.environ[config.lock_env_var]))
        try:
            yield _lock_state
        finally:
            _lock_state = _RELEASED
        return
    # Fresh acquisition: take the OS-level lock ourselves.
    config.workspace_dir.mkdir(parents=True, exist_ok=True)
    # Open without truncation so the existing holder's PID survives a failed acquire attempt.
    fd = _workspace_lock_file().open('a+')
    try:
        try:
            fcntl.flock(fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            fd.seek(0)
            holder = fd.read().strip()
            _lock_state = LockState(acquired=False, inherited=False,
                                    pid_of_holder=int(holder) if holder.isdigit() else None)
        else:
            pid = os.getpid()
            fd.seek(0)
            fd.truncate()
            fd.write(str(pid))
            fd.flush()
            os.environ[config.lock_env_var] = str(pid)
            _lock_state = LockState(acquired=True, inherited=False, pid_of_holder=pid)
        yield _lock_state
    finally:
        if _lock_state.acquired:
            fcntl.flock(fd.fileno(), fcntl.LOCK_UN)
            os.environ.pop(config.lock_env_var, None)
        fd.close()
        _lock_state = _RELEASED


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


def check_workspace_lock_generic[**P, T](func: Callable[P, T | None]) -> Callable[P, T | None]:
    """
    Decorator that guards a *non-command* helper against running without the workspace lock.

    For helpers that return domain data rather than an `int` exit code: if the workspace is
    not locked, an error is printed and the call is skipped, returning `None` in place of the
    wrapped function's normal result (so its return type widens to `T | None`).  Commands,
    which must return an `int` exit code, should use :func:`check_workspace_lock_command`.
    """
    from solver.shell import console

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T | None:
        if not (_lock_state.acquired or _lock_state.inherited):
            console.print(f'[error]Workspace is not locked!{_lock_state.held_by}[/error]')
            return None
        return func(*args, **kwargs)

    wrapper.__check_workspace_lock__ = True  # type: ignore[attr-defined]
    return wrapper


def check_workspace_lock_command[**P](func: Callable[P, int]) -> Callable[P, int]:
    """
    Decorator that guards a *command* against being called without holding the workspace lock.

    Checks whether the lock is held by this process or an inherited ancestor, which is true
    only while inside an "acquire_workspace_lock" context that successfully acquired the lock.
    Wrapped commands must conform to the command contract (return an `int` exit code).
    """
    from solver.shell import console

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> int:
        if not (_lock_state.acquired or _lock_state.inherited):
            console.print(f'[error]Workspace is not locked!{_lock_state.held_by}[/error]')
            return ExitCodes.EXIT_ERROR
        return func(*args, **kwargs)

    wrapper.__check_workspace_lock__ = True  # type: ignore[attr-defined]
    return wrapper

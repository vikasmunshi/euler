#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Utilities for workspace locking using file-based locks."""
from __future__ import annotations

__all__ = ['acquire_workspace_lock', 'check_workspace_lock_generic', 'check_workspace_lock_command', 'lock_state']

import contextlib
import fcntl
import functools
import os
from pathlib import Path
from typing import Callable, Generator, NamedTuple

from solver.config import ExitCodes, config
from solver.shell import console


class LockState(NamedTuple):
    acquired: bool
    inherited: bool
    pid_of_holder: int | None

    @property
    def held_by(self) -> str:
        return f' (held by PID {self.pid_of_holder})' if self.pid_of_holder else ''


_RELEASED: LockState = LockState(acquired=False, inherited=False, pid_of_holder=None)
lock_state: LockState = _RELEASED


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
    global lock_state
    # Reentrant call: already inside an active context in this process; reuse it untouched.
    if lock_state.acquired or lock_state.inherited:
        yield lock_state
        return
    # Inherited: an ancestor already holds the flock (detected via the inherited env var).
    if _lock_held():
        lock_state = LockState(acquired=False, inherited=True, pid_of_holder=int(os.environ[config.lock_env_var]))
        try:
            yield lock_state
        finally:
            lock_state = _RELEASED
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
            lock_state = LockState(acquired=False, inherited=False,
                                   pid_of_holder=int(holder) if holder.isdigit() else None)
        else:
            pid = os.getpid()
            fd.seek(0)
            fd.truncate()
            fd.write(str(pid))
            fd.flush()
            os.environ[config.lock_env_var] = str(pid)
            lock_state = LockState(acquired=True, inherited=False, pid_of_holder=pid)
        yield lock_state
    finally:
        if lock_state.acquired:
            fcntl.flock(fd.fileno(), fcntl.LOCK_UN)
            os.environ.pop(config.lock_env_var, None)
        fd.close()
        lock_state = _RELEASED


def check_workspace_lock_generic[**P, T](func: Callable[P, T | None]) -> Callable[P, T | None]:
    """
    Decorator that guards a *non-command* helper against running without the workspace lock.

    For helpers that return domain data rather than an `int` exit code: if the workspace is
    not locked, an error is printed and the call is skipped, returning `None` in place of the
    wrapped function's normal result (so its return type widens to `T | None`).  Commands,
    which must return an `int` exit code, should use :func:`check_workspace_lock_command`.
    """

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T | None:
        if not (lock_state.acquired or lock_state.inherited):
            console.print(f'[error]Workspace is not locked!{lock_state.held_by}[/error]')
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

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> int:
        if not (lock_state.acquired or lock_state.inherited):
            console.print(f'[error]Workspace is not locked!{lock_state.held_by}[/error]')
            return ExitCodes.EXIT_ERROR
        return func(*args, **kwargs)

    wrapper.__check_workspace_lock__ = True  # type: ignore[attr-defined]
    return wrapper

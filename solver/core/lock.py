#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Utilities for workspace locking using file-based locks."""
from __future__ import annotations

import contextlib
import fcntl
import functools
import os
from typing import Callable, Generator, IO, Literal

from solver.config import config
from solver.core.problems import Problem
from solver.shell import console

_lock_fd: IO[str] | None = None
_lock_depth: int = 0


@contextlib.contextmanager
def acquire_workspace_lock() -> Generator[bool, None, None]:
    """
    Acquire an exclusive lock on the workspace directory for the duration of the context.

    Uses OS-level file locking (fcntl.flock) so the lock is released automatically if the
    process exits or crashes — stale locks are never left behind. Reentrant within a single
    process: nested calls increment a depth counter and release only on the outermost exit.

    Yields:
        True  if the lock is held (either newly acquired or already held by this process).
        False if the workspace is already locked by another process.
    """
    global _lock_fd, _lock_depth
    if _lock_depth > 0:
        _lock_depth += 1
        try:
            yield True
        finally:
            _lock_depth -= 1
        return
    config.workspace_dir.mkdir(parents=True, exist_ok=True)
    if config.workspace_dir.name.startswith('.'):
        lock_file = config.workspace_dir.with_suffix('.lock')
    else:
        lock_file = config.workspace_dir.parent / f'.{config.workspace_dir.name}.lock'
    # Open without truncation so the existing holder's PID survives a failed acquire attempt.
    fd = lock_file.open('a+')
    acquired: bool = False
    try:
        try:
            fcntl.flock(fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            pass
        else:
            acquired = True
            fd.seek(0)
            fd.truncate()
            fd.write(str(os.getpid()))
            fd.flush()
            _lock_fd = fd
            _lock_depth = 1
        yield acquired
    finally:
        if acquired:
            fcntl.flock(fd.fileno(), fcntl.LOCK_UN)
            _lock_depth = 0
            _lock_fd = None
        fd.close()


def check_workspace[**P, T](func: Callable[P, T]) -> Callable[P, T | Literal['ok', 'nok']]:
    """
    Decorates a function to enforce workspace lock and initialization checks before execution.

    This decorator ensures that the workspace is locked and properly initialized before
    allowing the wrapped function to execute. If the workspace is not locked, or if it has
    not been initialized, appropriate error messages are printed, and the function will return
    a failure response.
    """

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T | Literal['ok', 'nok']:
        if _lock_depth <= 0:
            console.print('[error]Workspace is not locked or locked by another process[/error]')
            return 'nok'
        if Problem.from_workspace() is None:
            console.print('[muted]Use [accent]init[/accent] to initialize the workspace first.[/muted]')
            return 'nok'
        return func(*args, **kwargs)

    return wrapper


def check_workspace_lock[**P, T](func: Callable[P, T]) -> Callable[P, T]:
    """
    Decorator that guards a function against being called without holding the workspace lock.

    Checks the module-level depth counter, which is non-zero only while inside an
    "acquire_workspace_lock" context that successfully acquired the lock.
    """

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        if _lock_depth <= 0:
            console.print('[error]Workspace is not locked or locked by another process[/error]')
            return 'nok'  # type: ignore[return-value]
        return func(*args, **kwargs)

    return wrapper


__all__ = ('acquire_workspace_lock', 'check_workspace', 'check_workspace_lock',)

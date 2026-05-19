#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Utilities for workspace locking using file-based locks."""
from __future__ import annotations

import contextlib
import fcntl
import functools
import os
from typing import Callable, Generator

from solver.core.config import config

workspace_lock_acquired: bool = False


@contextlib.contextmanager
def acquire_workspace_lock() -> Generator[bool, None, None]:
    """
    Acquire an exclusive lock on the workspace directory for the duration of the context.

    Uses OS-level file locking (fcntl.flock) so the lock is released automatically if the
    process exits or crashes — stale locks are never left behind.

    Yields:
        True  if the lock was acquired and the caller may safely proceed.
        False if the workspace is already locked by another process.
    """
    global workspace_lock_acquired
    config.workspace_dir.mkdir(parents=True, exist_ok=True)
    if config.workspace_dir.name.startswith('.'):
        lock_file = config.workspace_dir.with_suffix('.lock')
    else:
        lock_file = config.workspace_dir.parent / f'.{config.workspace_dir.name}.lock'
    fd = lock_file.open('w')
    try:
        fcntl.flock(fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        fd.write(str(os.getpid()))
        fd.flush()
        workspace_lock_acquired = True
    except OSError:
        pass
    try:
        yield workspace_lock_acquired
    finally:
        if workspace_lock_acquired:
            fcntl.flock(fd.fileno(), fcntl.LOCK_UN)
            workspace_lock_acquired = False
        fd.close()


def check_workspace_lock[**P, T](func: Callable[P, T]) -> Callable[P, T]:
    """
    Decorator that guards a function against being called without holding the workspace lock.

    Checks the module-level "workspace_lock_acquired" flag, which is set to "True" only
    while inside an "acquire_workspace_lock" context.

    Raises:
        RuntimeError: If the calling process has not entered "acquire_workspace_lock".
    """

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        if not workspace_lock_acquired:
            raise RuntimeError('Workspace is not locked or locked by another process')
        return func(*args, **kwargs)

    return wrapper


__all__ = ('acquire_workspace_lock', 'check_workspace_lock',)

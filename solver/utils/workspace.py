#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Utilities for workspace locking using file-based locks."""
from __future__ import annotations

from contextlib import contextmanager
from fcntl import LOCK_EX, LOCK_NB, LOCK_UN, flock
from functools import wraps
from os import getpid
from typing import Callable, Generator

from solver.core.config import Config

workspace_lock_acquired: bool = False


@contextmanager
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
    Config.workspace_dir.mkdir(parents=True, exist_ok=True)
    if Config.workspace_dir.name.startswith('.'):
        lock_file = Config.workspace_dir.with_suffix('.lock')
    else:
        lock_file = Config.workspace_dir.parent / f'.{Config.workspace_dir.name}.lock'
    fd = lock_file.open('w')
    try:
        flock(fd.fileno(), LOCK_EX | LOCK_NB)
        fd.write(str(getpid()))
        fd.flush()
        workspace_lock_acquired = True
    except OSError:
        pass
    try:
        yield workspace_lock_acquired
    finally:
        if workspace_lock_acquired:
            flock(fd.fileno(), LOCK_UN)
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

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        if not workspace_lock_acquired:
            raise RuntimeError('Workspace is not locked or locked by another process')
        return func(*args, **kwargs)

    return wrapper


def move_to_bin(*filename: str) -> None:
    """
    Move one or more files specified by their names to the bin directory defined in the configuration.

    Arguments:
        filename (str): One or more names of the files to be moved.
    """
    for fn in filename:
        try:
            Config.workspace_dir.joinpath(fn).move(Config.bin_dir / fn)
        except FileNotFoundError:
            pass


__all__ = ('acquire_workspace_lock', 'check_workspace_lock', 'move_to_bin')

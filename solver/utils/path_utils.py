#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Utility functions for file and directory operations. """
from __future__ import annotations

from pathlib import Path
from typing import Generator, Literal, overload

from solver.core.config import config
from solver.core.lock import check_workspace_lock
from solver.core.console import console


def canonical_path(path: Path) -> str:
    """Return a POSIX path string relative to root_dir."""
    return path.relative_to(config.root_dir).as_posix()


@overload
def iterdir_recursive(directory: Path, *,
                      rt: Literal['path'] = ...,
                      _root: Path | None = ...) -> Generator[Path, None, None]:
    ...


@overload
def iterdir_recursive(directory: Path, *,
                      rt: Literal['str'],
                      _root: Path | None = ...) -> Generator[str, None, None]:
    ...


def iterdir_recursive(directory: Path, *,
                      rt: Literal['path', 'str'] = 'path',
                      _root: Path | None = None, ) -> Generator[Path | str, None, None]:
    """Yield all files under the directory, returning Paths or POSIX strings relative to directory per rt."""
    if not directory.exists():
        return
    if directory.is_file():
        return
    root = _root or directory
    for item in directory.iterdir():
        if item.is_dir():
            yield from iterdir_recursive(item, rt=rt, _root=root)
        elif item.is_file():
            if rt == 'str':
                yield item.relative_to(root).as_posix()
            else:
                yield item


@check_workspace_lock
def write_file(path: Path, content: bytes, msg: str | None = None) -> None:
    """Write bytes to the path, creating parent directories as needed, and optionally print a status message."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    if msg is not None:
        console.print(f'[muted]{msg}, wrote {len(content)} bytes to [accent]{canonical_path(path)}[/accent][/muted]')


__all__ = (
    'canonical_path',
    'iterdir_recursive',
    'write_file',
)

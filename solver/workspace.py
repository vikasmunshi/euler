#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path
from shutil import rmtree
from typing import Generator

__all__ = [
    'BASE_DIR',
    'CACHE_DIR',
    'MANIFEST_FILENAME',
    'PROBLEMS_LIST_URL',
    'PROJECTEULER_URL',
    'STACK_DIR',
    'WORKSPACE_DIR',
    'clear_workspace',
    'iterdir_recursive',
    'write_file',
]

# Path constants
BASE_DIR: Path = Path.cwd()  # Project root directory
CACHE_DIR: Path = BASE_DIR / 'cache'
STACK_DIR: Path = BASE_DIR / 'stack'  # Base stack directory
WORKSPACE_DIR: Path = BASE_DIR / 'workspace'  # Working/temporary files directory
MANIFEST_FILENAME: str = 'manifest.txt'

# URL constants
PROJECTEULER_URL: str = 'https://projecteuler.net'
PROBLEMS_LIST_URL: str = f'{PROJECTEULER_URL}/minimal=problems'


def clear_workspace() -> None:
    """Clear the workspace directory."""
    print('Clearing workspace')
    rmtree(WORKSPACE_DIR, ignore_errors=True)


def iterdir_recursive(directory: Path) -> Generator[Path, None, None]:
    if not directory.exists():
        return None
    if directory.is_file():
        yield directory
        return None
    for path in directory.iterdir():
        if path.is_dir():
            yield from iterdir_recursive(path)
        elif path.is_file():
            yield path
    return None


def write_file(path: Path, content: bytes, verbose: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    if verbose:
        print(f'Wrote {len(content)} bytes to {path}')

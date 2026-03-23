#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Workspace and directory management utilities."""
from __future__ import annotations

from pathlib import Path
from shutil import rmtree
from typing import Generator

__all__ = [
    'BACKUP_DIR',
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

# ============================================================================
# Constants
# ============================================================================

# Path constants
BASE_DIR: Path = Path.cwd()  # Project root directory
CACHE_DIR: Path = BASE_DIR / 'cache'
STACK_DIR: Path = BASE_DIR / 'stack'  # Base stack directory
WORKSPACE_DIR: Path = BASE_DIR / 'workspace'  # Working/temporary files directory
BACKUP_DIR: Path = BASE_DIR / 'backup' # Backup directory
MANIFEST_FILENAME: str = 'manifest.txt'

# URL/Contact constants
PROJECTEULER_URL: str = 'https://projecteuler.net'
PROBLEMS_LIST_URL: str = f'{PROJECTEULER_URL}/minimal=problems'


# ============================================================================
# Workspace Management
# ============================================================================

def clear_workspace() -> None:
    """Clear the workspace directory."""
    print('Clearing workspace')
    rmtree(WORKSPACE_DIR, ignore_errors=True)


# ============================================================================
# File Operations
# ============================================================================

def iterdir_recursive(directory: Path) -> Generator[Path, None, None]:
    """Recursively iterate over all files in a directory.

    Args:
        directory: Directory to iterate over

    Yields:
        Path objects for each file found
    """
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
    """Write content to file, creating parent directories if needed.

    Args:
        path: File path to write to
        content: Byte content to write
        verbose: Print a confirmation message if True
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    if verbose:
        print(f'Wrote {len(content)} bytes to {path}')

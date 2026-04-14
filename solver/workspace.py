#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Workspace and directory management utilities."""
from __future__ import annotations

from pathlib import Path
from shutil import rmtree
from typing import Generator

__all__ = [
    'admin_user',
    'backup_dir',
    'base_dir',
    'cache_dir',
    'clear_workspace',
    'crypto_dir',
    'iterdir_recursive',
    'keys_file',
    'keys_version',
    'manifest_filename',
    'package_dir',
    'private_key_file',
    'problems_list_url',
    'projecteuler_url',
    'push_script_path',
    'repo_https',
    'repo_ssh',
    'sample_cipher_text_file',
    'sample_plain_text_file',
    'schema_file',
    'stack_dir',
    'workspace_dir',
    'write_file',
]

# ============================================================================
# Constants
# ============================================================================

# Paths and constants
base_dir: Path = Path.cwd()  # Project root directory
package_dir: Path = Path(__file__).parent
crypto_dir: Path = package_dir / 'crypto'
repo_https: str = 'https://github.com/vikasmunshi/euler.git'
repo_ssh: str = 'git@github.com:vikasmunshi/euler.git'

admin_user: str = 'vikas.munshi@gmail.com'
backup_dir: Path = base_dir / 'backup'  # Backup directory
cache_dir: Path = base_dir / 'cache'
keys_file: Path = crypto_dir / 'keys.json'
keys_version: str = '1.0.1'
manifest_filename: str = 'manifest.txt'
private_key_file: Path = Path.home() / '.ssh' / 'id_x25519.json'
push_script_path: Path = crypto_dir / 'keys.sh'
sample_cipher_text_file: Path = crypto_dir / 'text_cipher.txt'
sample_plain_text_file: Path = crypto_dir / 'text_plain.txt'
schema_file: Path = crypto_dir / 'keys.schema.json'
stack_dir: Path = package_dir / 'stack'  # Base stack directory
workspace_dir: Path = base_dir / 'workspace'  # Working/temporary files directory

# URL/Contact
projecteuler_url: str = 'https://projecteuler.net'
problems_list_url: str = f'{projecteuler_url}/minimal=problems'


# ============================================================================
# Workspace Management
# ============================================================================

def clear_workspace() -> None:
    """Clear the workspace directory."""
    print('Clearing workspace')
    rmtree(workspace_dir, ignore_errors=True)


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
    verbose and print(f'Wrote {len(content)} bytes to {path}')

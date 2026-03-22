#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Stack management for storing and retrieving problem workspaces.

Manages encrypted storage of Project Euler problem workspaces with integrity verification.

## Public API

    read_manifest(problem_number) -> dict[str, str]
        Get filename-to-hash mappings for a problem's stack

    read_stack_file(problem_number, filename) -> bytes | None
        Read and decrypt a file from stack storage

    stack_from_workspace(process_deletions=False) -> bool
        Save current workspace to stack with encryption and verification

    unstack_to_workspace(problem_number, *, re_init=False, force_refresh=False) -> None
        Restore workspace from stack, optionally re-initializing from Project Euler

## Encryption Strategy

    Public problems (≤100):  Stored as plaintext
    Private problems (>100):
        - Project Euler files:  Stored as plaintext (publicly available)
        - User solutions:       AES-256-GCM encrypted with AAD binding

    AAD format:  'euler-solver-stack-{problem_number}-{filename}'.encode()
    File naming: Encrypted files get '.enc' suffix in stack

## Manifest Format

    Each line: {sha256_hash} {filename}
    Purpose:   Integrity verification and change detection
    Location:  stack/{problem}/manifest.txt

## Directory Structure

    stack/
    └── {problem_number}/         # e.g., 0/1/2/3/ for problem 123
        ├── manifest.txt          # Hash-to-filename mappings
        ├── problem.txt           # Public: stored plaintext
        ├── solution.py.enc       # Private: encrypted user code
        └── notes.md.enc          # Private: encrypted user notes

Author: Vikas Munshi <vikas.munshi@gmail.com>
Repository: https://github.com/vikasmunshi/euler
"""
from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

from solver.projecteuler import ProjectEulerFiles, init_from_projecteuler
from solver.vault import decrypt, encrypt
from solver.workspace import MANIFEST_FILENAME, STACK_DIR, WORKSPACE_DIR, iterdir_recursive, write_file

__all__ = ['read_manifest', 'read_stack_file', 'stack_from_workspace', 'unstack_to_workspace']


# ============================================================================
# Manifest Operations
# ============================================================================

def read_manifest(problem_number: int) -> dict[str, str]:
    """Read manifest file mapping filenames to content hashes.

    Args:
        problem_number: Project Euler problem number

    Returns:
        Dict mapping filename to SHA-256 hex digest (empty dict if not found)
    """
    manifest_file: Path = _stack_dir(problem_number) / MANIFEST_FILENAME
    try:
        return dict(line.split(' ', 1)[::-1] for line in manifest_file.read_text().splitlines() if line)
    except FileNotFoundError:
        print(f'Warning: Manifest file {manifest_file} not found, returning empty manifest')
        return {}


# ============================================================================
# Stack File Operations
# ============================================================================

def read_stack_file(problem_number: int, filename: str) -> bytes | None:
    """Read and decrypt a file from stack storage.

    Args:
        problem_number: Project Euler problem number
        filename: Relative path in workspace (e.g., 'solution.py', 'notes/ideas.md')

    Returns:
        Decrypted file content, or None if not found or authentication failed

    Note:
        Automatically handles decryption for private problems (>100) with AAD binding.
    """
    encryption_required, stack_path = _stack_path(problem_number, filename)
    try:
        content: bytes = stack_path.read_bytes()
    except FileNotFoundError:
        print(f'Error: stack file {stack_path} not found, returning null')
        return None
    if encryption_required:
        try:
            content = decrypt(content, aad=_associated_authentication_data(problem_number, filename))
        except ValueError as e:
            print(f'Error: Invalid content in stack file {stack_path}, returning null. error: {e}')
            return None
    return content


# ============================================================================
# Stack/Unstack Operations
# ============================================================================

def stack_from_workspace(process_deletions: bool = False) -> bool:
    """Save the current workspace to stack with encryption and verification.

    Args:
        process_deletions: If True, remove stack files deleted from workspace

    Returns:
        True if all stack files pass hash verification after stacking

    Note:
        - Skips files with unchanged SHA-256 hashes
        - Auto-encrypts private problem solutions with AAD binding
        - Updates manifest with new/modified file hashes
    """
    if (problem_number := ProjectEulerFiles.current_problem_number()) is None:
        print('Warning: No problem number found in workspace, nothing to do.')
        return False
    print(f'Stacking workspace for problem {problem_number}...')
    manifest: dict[str, str] = read_manifest(problem_number)
    files: set[Path] = set(iterdir_recursive(WORKSPACE_DIR))
    for filepath in files:
        filename: str = filepath.relative_to(WORKSPACE_DIR).as_posix()
        content: bytes = filepath.read_bytes()
        content_hash: str = sha256(content).hexdigest()
        if filename in manifest and manifest[filename] == content_hash:
            print(f'Skipping {filename} (no changes in content)')
            continue
        _write_stack_file(problem_number, filename, content)
        manifest[filename] = content_hash
        print(f'Added file {filename} to stack and manifest')
    if process_deletions:
        for file in set(manifest.keys()) - set(f.relative_to(WORKSPACE_DIR).as_posix() for f in files):
            _delete_stack_file(problem_number, file)
            del manifest[file]
            print(f'Deleted {file} from stack and manifest')
    _write_manifest(problem_number, manifest)
    print('Stacking complete')
    return _verify_manifest(problem_number)


def unstack_to_workspace(problem_number: int, *, re_init: bool = False, force_refresh: bool = False) -> None:
    """Restore the workspace from stack storage.

    Args:
        problem_number: Project Euler problem number to restore
        re_init: Force re-initialization from Project Euler website
        force_refresh: Force re-download even if cached (requires re_init=True)

    Note:
        - Refuses to overwrite existing workspace for different problem
        - Auto re-initializes if Project Euler files are missing
        - Decrypts private files automatically using AAD verification
    """
    if (current := ProjectEulerFiles.current_problem_number()) and current != problem_number:
        print(f'Error: workspace already exists for problem {current}, clear before unstacking {problem_number}')
        return
    print(f'Initializing workspace for problem {problem_number}...')
    for filename, content_hash in read_manifest(problem_number).items():
        if (content := read_stack_file(problem_number, filename)) is not None:
            target_file: Path = WORKSPACE_DIR / filename
            write_file(target_file, content)
            print(f'Copied {filename} to {target_file}')
    re_init = re_init or any(not (WORKSPACE_DIR / filename.value).exists()
                             for filename in ProjectEulerFiles
                             if filename != ProjectEulerFiles.problem_resources_dir)
    if re_init:
        init_from_projecteuler(problem_number, force_refresh=force_refresh)
    print('Unstacking complete')


# ============================================================================
# Private Helper Functions
# ============================================================================

def _delete_stack_file(problem_number: int, filename: str) -> None:
    """Delete the file from the stack and clean up empty directories.

    Args:
        problem_number: Problem number
        filename: Relative filename in stack
    """
    _, stack_path = _stack_path(problem_number, filename)
    try:
        stack_path.unlink()
    except FileNotFoundError:
        print(f'Error: stack file {stack_path} not found, skipping deletion.')
    try:
        stack_path.parent.rmdir()
    except OSError:
        pass


@lru_cache(maxsize=None)
def _stack_path(problem_number: int, filename: str) -> tuple[bool, Path]:
    """Determines the stack path and encryption requirement for a given file.

    Args:
        problem_number: Problem number
        filename: Relative filename in stack
        
    Returns:
        tuple[bool, Path]: (encryption_required, stack_path)

    """
    encryption_required: bool = _is_private(problem_number) and not _is_public(filename)
    stack_path: Path = _stack_dir(problem_number) / (filename + '.enc' if encryption_required else filename)
    return encryption_required, stack_path


@lru_cache(maxsize=None)
def _associated_authentication_data(problem_number: int, filename: str) -> bytes:
    """Get the associated authentication data for a file in the stack.

    Args:
        problem_number: Problem number
        filename: Relative filename

    Returns:
        Associated Authentication Data (AAD) bytes
    """
    return f'euler-solver-stack-{problem_number}-{filename}'.encode()


@lru_cache(maxsize=None)
def _is_private(problem_number: int) -> bool:
    """Check if the problem requires encryption (problem > 100).

    Args:
        problem_number: Problem number

    Returns:
        True if the problem is private
    """
    return problem_number > 100


@lru_cache(maxsize=None)
def _is_public(filename: str) -> bool:
    """Check if the file is a public Project Euler file.

    Args:
        filename: Relative filename

    Returns:
        True if the file is public
    """
    return filename.split('/')[0] in ProjectEulerFiles


@lru_cache(maxsize=None)
def _stack_dir(problem_number: int) -> Path:
    """Get the stack directory path for the problem.

    Args:
        problem_number: Problem number

    Returns:
        Path to stack directory
    """
    return STACK_DIR.joinpath(*f'{problem_number:04d}')


def _verify_manifest(problem_number: int) -> bool:
    """Verify stack files match manifest hashes.

    Args:
        problem_number: Problem number

    Returns:
        True if all files are valid
    """
    results: dict[str, list[str]] = defaultdict(list)
    manifest: dict[str, str] = read_manifest(problem_number)
    for filename, expected_hash in manifest.items():
        if (content := read_stack_file(problem_number, filename)) is None:
            results['error'].append(filename)
        elif expected_hash == sha256(content).hexdigest():
            results['valid'].append(filename)
        else:
            results['modified'].append(filename)
    stack_path: Path = _stack_dir(problem_number)
    for file_path in iterdir_recursive(stack_path):
        if file_path.name == MANIFEST_FILENAME:
            continue
        filename = file_path.relative_to(stack_path).as_posix()
        if filename.endswith('.enc'):
            filename = filename[:-4]
        if filename not in manifest:
            results['untracked'].append(filename)
    valid_filenames: list[str] = results.pop('valid', [])
    if results or not valid_filenames:
        print(f'Error: stack verification failed for problem {problem_number}.')
        for status, filenames in results.items():
            print(f'{status}: {", ".join(filenames)}')
        print(f'Valid files: {", ".join(valid_filenames)}')
        return False
    print(f'Stack verification passed for problem {problem_number}.')
    return True


def _write_manifest(problem_number: int, manifest: dict[str, str]) -> None:
    """Write the manifest file containing the filename to hash mappings.

    Args:
        problem_number: Problem number
        manifest: Dict mapping filename to SHA-256 hash
    """
    manifest_file: Path = _stack_dir(problem_number) / MANIFEST_FILENAME
    write_file(manifest_file, b'\n'.join(f'{v} {k}'.encode() for k, v in manifest.items()))


def _write_stack_file(problem_number: int, filename: str, content: bytes) -> None:
    """Write the file to stack, encrypting if necessary.

    Args:
        problem_number: Problem number
        filename: Relative filename in stack
        content: File content to write
    """
    encryption_required, stack_path = _stack_path(problem_number, filename)
    if encryption_required:
        content = encrypt(content, aad=_associated_authentication_data(problem_number, filename))
    write_file(stack_path, content)

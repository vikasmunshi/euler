#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Stack directory management: file read/write, transparent encryption, and path resolution."""
from __future__ import annotations

from functools import lru_cache
from os import X_OK, access
from pathlib import Path
from shutil import rmtree
from typing import TYPE_CHECKING

from solver.config import (backup_dirname, root_dir, problem_number_filename, problem_statement_filename,
                           resource_dirname, stack_dir)
from solver.problems import problems
from solver.utils import iterdir_recursive, write_file

if TYPE_CHECKING:
    from solver.crypto.symmetrical import EncKey

__all__ = [
    'backup_the_stack',
    'read_stack_file',
    'restore_the_stack',
    'stack',
    'stack_base_dir',
    'stack_path',
    'unstack',
    'write_stack_file',
]


@lru_cache(maxsize=None)
def get_enc_key(key_id: bytes | None = None) -> EncKey:
    """
    Look up an encryption key, returning the active key when no ID is given.

    Args:
        key_id: Raw 16-byte key identifier. If None, the current active key is returned.

    Returns:
        The EncKey matching the given ID, or the active key if key_id is None.
    """
    from solver.crypto.keys import get_key
    if key_id is None:
        return get_key()
    else:
        return get_key(key_id.hex())


@lru_cache(maxsize=None)
def stack_base_dir(problem_number: int) -> Path:
    """Return the stack directory for a problem, rooted one digit-level deep per digit of its zero-padded number."""
    return stack_dir.joinpath(*f'{problem_number:04d}')


@lru_cache(maxsize=None)
def stack_path(problem_number: int, filename: str) -> tuple[bool, Path]:
    """
    Resolve the on-disk path for a stack file and determine whether it must be encrypted.

    Encryption is required for all files belonging to problems above 100, except for
    the problem number file, problem statement (Markdown and HTML), and resource files.

    Args:
        problem_number: The Project Euler problem number.
        filename:       Logical filename within the problem's stack directory (without .enc suffix).

    Returns:
        A 2-tuple of (encryption_required, path), where the path already includes the .enc
        suffix when encryption is required.
    """
    encryption_required: bool = not (
            problem_number <= 100
            or filename == problem_number_filename
            or filename == problem_statement_filename
            or filename == problem_statement_filename
            or filename.startswith(resource_dirname)
    )
    stack_file_path: Path = stack_base_dir(problem_number) / (filename + '.enc' if encryption_required else filename)
    return encryption_required, stack_file_path


def read_stack_file(problem_number: int, filename: str) -> tuple[bytes, bool]:
    """
    Read a file from the stack, decrypting it if required.

    Args:
        problem_number: The Project Euler problem number.
        filename:       Logical filename within the problem's stack directory.

    Returns:
        A 2-tuple of (content, is_executable), where content is the decrypted file bytes
        and is_executable reflects the file's 'execute' permission bit.

    Raises:
        FileNotFoundError: If the stack file does not exist.
    """
    encryption_required, stack_file_path = stack_path(problem_number, filename)
    content: bytes = stack_file_path.read_bytes()
    is_executable: bool = access(stack_file_path, X_OK)
    if encryption_required:
        key_id, enc_content = content[:16], content[16:]
        key = get_enc_key(key_id)
        content = key.decrypt(enc_content, aad=filename.encode())
    return content, is_executable


def write_stack_file(problem_number: int, filename: str, content: bytes, is_executable: bool) -> None:
    """
    Write a file to the stack, encrypting it if required.

    Encrypted files are prefixed with the 16-byte key ID so the correct key can be
    looked up at read time.

    Args:
        problem_number: The Project Euler problem number.
        filename:       Logical filename within the problem's stack directory.
        content:        Raw file bytes to write (plaintext; encryption is applied automatically).
        is_executable:  If True, the file's 'execute' permission bit (0o755) is set after writing.
    """
    try:
        stack_content: bytes | None = read_stack_file(problem_number, filename)[0]
    except (FileNotFoundError, ValueError):
        stack_content = None
    if stack_content and stack_content == content:
        return
    encryption_required, stack_file_path = stack_path(problem_number, filename)
    if encryption_required:
        key = get_enc_key()
        content = bytes.fromhex(key.id) + key.encrypt(content, aad=filename.encode())  # first 16 bytes are key id
    write_file(stack_file_path, content)
    if is_executable:
        stack_file_path.chmod(0o755)


def stack(problem_number: int, workspace_dir: Path) -> None:
    """
    Read all files from the workspace directory and write them into the stack, encrypting as required.
    This is the inverse of 'unstack'; executable bits are preserved.

    Args:
        problem_number: The Project Euler problem number.
        workspace_dir:  Source directory containing the plaintext backup files.
    """
    for workspace_file_path in iterdir_recursive(workspace_dir):
        filename: str = workspace_file_path.relative_to(workspace_dir).as_posix()
        content: bytes = workspace_file_path.read_bytes()
        if not filename.startswith(resource_dirname):
            try:
                content.decode()
            except UnicodeDecodeError:
                continue
        is_executable: bool = access(workspace_file_path, X_OK)
        write_stack_file(problem_number, filename, content, is_executable)


def unstack(problem_number: int, workspace_dir: Path) -> None:
    """
    Read all files from the stack and write them into the workspace, decrypting as required.
    This is the inverse of 'stack'; executable bits are preserved.

    Args:
        problem_number: The Project Euler problem number.
        workspace_dir:  Destination directory; intermediate directories are created as needed.
    """
    problem_stack_dir: Path = stack_base_dir(problem_number)
    for filename in iterdir_recursive(problem_stack_dir, rt='str'):
        filename = filename.removesuffix('.enc')
        content, is_executable = read_stack_file(problem_number, filename)
        workspace_file_path: Path = workspace_dir.joinpath(filename)
        write_file(workspace_file_path, content)
        if is_executable:
            workspace_file_path.chmod(0o755)


def backup_the_stack() -> None:
    """
    Back up problem files from the stack to the 'backup' folder (unencrypted).
    Ensures '/backup/' is listed in .gitignore, then iterates over all problems,
    decrypting and copying their stack files into backup/<one digit-level per digit of zero-padded problem number>/.
    """
    try:
        gitignore: str = root_dir.joinpath('.gitignore').read_text()
    except FileNotFoundError:
        gitignore = ''
    if f'/{backup_dirname}/' not in gitignore:
        root_dir.joinpath('.gitignore').write_text(gitignore.strip('\n') + f'\n/{backup_dirname}/\n')
    for problem in problems:
        problem_backup_dir = root_dir.joinpath(backup_dirname, *f'{problem.number:04d}')
        problem_stack_dir: Path = stack_base_dir(problem.number)
        if not problem_stack_dir.exists():
            print(f'No stack found for "{problem.number}: {problem.title}"')
            continue
        if problem_backup_dir.exists():
            rmtree(problem_backup_dir, ignore_errors=True)
        unstack(problem.number, workspace_dir=problem_backup_dir)
        print(f'Created backup for "{problem!s}": {problem_backup_dir.relative_to(root_dir).as_posix()}')


def restore_the_stack() -> None:
    """
    Restore problem files from the 'backup' folder (unencrypted) to the stack (encrypted).
    Inverse of 'backup_the_stack'.
    """
    for problem in problems:
        problem_backup_dir = root_dir.joinpath(backup_dirname, *f'{problem.number:04d}')
        problem_stack_dir: Path = stack_base_dir(problem.number)
        if not problem_backup_dir.exists():
            print(f'No backup found for "{problem!s}"')
            continue
        stack(problem.number, workspace_dir=problem_backup_dir)
        print(f'Restored backup for "{problem!s}": {problem_stack_dir.relative_to(root_dir).as_posix()}')

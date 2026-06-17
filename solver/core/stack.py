#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Stack directory management: file read/write, transparent encryption, and path resolution."""
from __future__ import annotations

__all__ = [
    'backup_the_solutions_stack',
    'notes_are_stale',
    'read_stack_file',
    'restore_the_solutions_stack',
    'stack_base_dir',
    'stack_path',
    'stack_to_solutions',
    'unstack_from_solutions',
    'write_stack_file',
]

from base64 import b64decode, b64encode
from functools import lru_cache
from json import JSONDecodeError, dumps, loads
from os import X_OK, access, utime
from pathlib import Path
from typing import Any

from solver.config import config
from solver.core.lock import check_workspace_lock_generic
from solver.core.problems import problems
from solver.crypto.keys import get_enc_key
from solver.shell import console
from solver.shell.variables import variables
from solver.utils.path_utils import canonical_path, iterdir_recursive, write_file
from solver.utils.shell_utils import confirm, run_command


@lru_cache(maxsize=None)
def stack_base_dir(problem_number: int) -> Path:
    """Return the stack directory for a problem, rooted one digit-level deep per digit of its zero-padded number."""
    return config.solutions_dir.joinpath(*f'{problem_number:04d}')


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
            or filename == config.number_filename
            or filename == config.statement_filename
            or filename.startswith(config.resource_dirname)
    )
    stack_file_path: Path = stack_base_dir(problem_number) / (filename + '.enc' if encryption_required else filename)
    return encryption_required, stack_file_path


def notes_are_stale(problem_number: int) -> bool:
    """Return True if the problem's notes.html is missing or meaningfully older than its solution sources.

    This is the exact condition a `document` / `summarise` review reacts to: the prose post-dates a
    code change, so the notes need refreshing.  The check compares the on-disk mtimes of the stack
    files, so it works transparently for encrypted (problem > 100) stacks without decrypting anything;
    only the top-level `.py` / `.c` sources are considered (resources live in a subdirectory), and a
    source must lead notes.html by more than NOTES_STALE_TOLERANCE_S to count (so same-write
    formatting jitter does not register).
    """
    base: Path = stack_base_dir(problem_number)
    if not base.is_dir():
        return False
    _, notes_path = stack_path(problem_number, config.notes_filename)
    if not notes_path.exists():
        return True
    cutoff: float = notes_path.stat().st_mtime + config.stale_notes_tolerance_s
    return any(
        path.name.removesuffix('.enc').endswith(('.py', '.c')) and path.stat().st_mtime > cutoff
        for path in base.iterdir()
        if path.is_file()
    )


def read_stack_file(problem_number: int, filename: str) -> tuple[bytes, bool, float]:
    """
    Read a file from the stack, decrypting it if required.

    Args:
        problem_number: The Project Euler problem number.
        filename:       Logical filename within the problem's stack directory.

    Returns:
        A 3-tuple of (content, is_executable, m_time), where content is the decrypted file bytes,
        is_executable reflects the file's 'execute' permission bit, and m_time is the file's modification time.

    Raises:
        FileNotFoundError: If the stack file does not exist.
        KeyError:          If the stack file is encrypted but the corresponding key is not found.
        ValueError:        If the stack file is encrypted but cannot be decrypted for any reason.
    """
    encryption_required, stack_file_path = stack_path(problem_number, filename)
    content: bytes = stack_file_path.read_bytes()
    is_executable: bool = access(stack_file_path, X_OK)
    m_time: float = stack_file_path.stat().st_mtime
    if encryption_required:
        content = b64decode(content, validate=True)
        key_id, enc_content = content[:16], content[16:]  # first 16 bytes are key id
        key = get_enc_key(key_id)
        content = key.decrypt(enc_content, aad=filename.encode())
    return content, is_executable, m_time


@check_workspace_lock_generic
def write_stack_file(problem_number: int, filename: str, content: bytes, is_executable: bool, m_time: float) -> None:
    """
    Write a file to the stack, encrypting it if required.

    Encrypted files are prefixed with the 16-byte key ID so the correct key can be
    looked up at read time.

    Args:
        problem_number: The Project Euler problem number.
        filename:       Logical filename within the problem's stack directory.
        content:        Raw file bytes to write (plaintext; encryption is applied automatically).
        is_executable:  If True, the file's 'execute' permission bit (0o755) is set after writing.
        m_time:         Modification time of the file to be written
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
        content = b64encode(content)
    write_file(stack_file_path, content)
    if is_executable:
        stack_file_path.chmod(0o755)
    utime(stack_file_path, (m_time, m_time))


# ==================================================================================================================== #
#                                               stack / unstack
# ==================================================================================================================== #
@check_workspace_lock_generic
def stack_to_solutions(problem_number: int) -> None:
    """
    Read all files from the workspace directory and write them into the stack, encrypting as required.
    This is the inverse of 'unstack'; executable bits are preserved.

    Args:
        problem_number: The Project Euler problem number.
    """
    if (problem := variables.problem) is None:
        console.print('[muted]Use [accent]init[/accent] to initialize the workspace first.[/muted]')
        return
    if problem_number != problem.number:
        console.print(f'[error]Problem {problem_number} is not the current problem![/error]')
        return
    for workspace_file_path in iterdir_recursive(config.workspace_dir):
        filename: str = workspace_file_path.relative_to(config.workspace_dir).as_posix()
        content: bytes = workspace_file_path.read_bytes()
        if not filename.startswith(config.resource_dirname):
            try:
                content.decode()
            except UnicodeDecodeError:
                continue  # exclude not text files, except in the resources directory
        if filename.endswith('.json'):
            try:
                obj: Any = loads(content)
                content = dumps(obj, indent=2).encode()
            except JSONDecodeError:
                console.print(f'[error]Failed to parse JSON file {canonical_path(workspace_file_path)}!', style='bold')
                continue  # exclude invalid json files
        is_executable: bool = access(workspace_file_path, X_OK)
        m_time: float = workspace_file_path.stat().st_mtime
        write_stack_file(problem_number, filename, content, is_executable, m_time)


@check_workspace_lock_generic
def unstack_from_solutions(problem_number: int) -> None:
    """
    Read all files from the stack and write them into the workspace, decrypting as required.
    This is the inverse of 'stack'; executable bits are preserved.

    Args:
        problem_number: The Project Euler problem number.
    """
    if (problem := variables.problem) is not None and problem_number != problem.number:
        console.print(f'[error]Problem {problem_number} is not the current problem![/error]')
        return
    problem_stack_dir: Path = stack_base_dir(problem_number)
    for filename in iterdir_recursive(problem_stack_dir, rt='str'):
        filename = filename.removesuffix('.enc')
        content, is_executable, m_time = read_stack_file(problem_number, filename)
        workspace_file_path: Path = config.workspace_dir.joinpath(filename)
        write_file(workspace_file_path, content)
        if is_executable:
            workspace_file_path.chmod(0o755)
        utime(workspace_file_path, (m_time, m_time))


# ==================================================================================================================== #
#                                               backup / restore
# ==================================================================================================================== #
def backup_the_solutions_stack() -> None:
    """
    Back up problem files from the stack to the 'backup' folder (unencrypted).
    Raises RuntimeError if the backup directory is not git-ignored (checked via 'git check-ignore').
    Then iterates over all problems, decrypting and copying their stack files into
    backup/<one digit-level per digit of zero-padded problem number>/.
    """
    if run_command(f'git check-ignore -q {config.backup_dir.name}', silent=True) is None:
        raise RuntimeError(f'Backup directory {config.backup_dir.name} is not ignored by git')
    orig_workspace_dir = config.backup_dir
    try:
        for problem_number in range(1, problems.problems_list[-1].number + 1):
            config.workspace_dir = config.backup_dir / stack_base_dir(problem_number).relative_to(config.solutions_dir)
            unstack_from_solutions(problem_number)
            console.print(f'[muted]Stack backup for problem [accent]{problem_number}[/accent] → '
                          f'{canonical_path(config.workspace_dir)}[/muted]')
    finally:
        config.workspace_dir = orig_workspace_dir


def restore_the_solutions_stack() -> None:
    """
    Restore problem files from the 'backup' folder (unencrypted) to the stack (encrypted).
    Inverse of 'backup_the_stack'.
    """
    if not confirm('Are you sure, you want to restore the stack?'):
        console.print('[muted]Stack restoration cancelled.[/muted]')
        return
    orig_workspace_dir = config.backup_dir
    try:
        for problem_number in range(1, problems.problems_list[-1].number + 1):
            config.workspace_dir = config.backup_dir / stack_base_dir(problem_number).relative_to(config.solutions_dir)
            stack_to_solutions(problem_number)
            console.print(f'[muted]Stack restored for problem [accent]{problem_number}[/accent] ← '
                          f'{canonical_path(config.workspace_dir)}[/muted]')
    finally:
        config.workspace_dir = orig_workspace_dir

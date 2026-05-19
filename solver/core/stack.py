#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Stack directory management: file read/write, transparent encryption, and path resolution."""
from __future__ import annotations

from functools import lru_cache
from json import JSONDecodeError, dumps, loads
from os import X_OK, access, utime
from pathlib import Path
from typing import Any

from solver.core.config import config
from solver.core.lock import check_workspace_lock
from solver.core.problems import problems
from solver.crypto.keys import get_enc_key
from solver.core.console import console, register
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
            or filename == config.statement_filename
            or filename.startswith(config.resource_dirname)
    )
    stack_file_path: Path = stack_base_dir(problem_number) / (filename + '.enc' if encryption_required else filename)
    return encryption_required, stack_file_path


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
    """
    encryption_required, stack_file_path = stack_path(problem_number, filename)
    content: bytes = stack_file_path.read_bytes()
    is_executable: bool = access(stack_file_path, X_OK)
    m_time: float = stack_file_path.stat().st_mtime
    if encryption_required:
        key_id, enc_content = content[:16], content[16:]  # first 16 bytes are key id
        key = get_enc_key(key_id)
        content = key.decrypt(enc_content, aad=filename.encode())
    return content, is_executable, m_time


@check_workspace_lock
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
    write_file(stack_file_path, content)
    if is_executable:
        stack_file_path.chmod(0o755)
    utime(stack_file_path, (m_time, m_time))


# ==================================================================================================================== #
#                                               stack / unstack
# ==================================================================================================================== #

def stack(problem_number: int) -> None:
    """
    Read all files from the workspace directory and write them into the stack, encrypting as required.
    This is the inverse of 'unstack'; executable bits are preserved.

    Args:
        problem_number: The Project Euler problem number.
    """
    for workspace_file_path in iterdir_recursive(config.workspace_dir):
        filename: str = workspace_file_path.relative_to(config.workspace_dir).as_posix()
        content: bytes = workspace_file_path.read_bytes()
        if not filename.startswith(config.resource_dirname):
            try:
                content.decode()
            except UnicodeDecodeError:
                continue
        if filename.endswith('.json'):
            try:
                obj: Any = loads(content)
                content = dumps(obj, indent=2).encode()
            except JSONDecodeError:
                continue
        is_executable: bool = access(workspace_file_path, X_OK)
        m_time: float = workspace_file_path.stat().st_mtime
        write_stack_file(problem_number, filename, content, is_executable, m_time)


def unstack(problem_number: int) -> None:
    """
    Read all files from the stack and write them into the workspace, decrypting as required.
    This is the inverse of 'stack'; executable bits are preserved.

    Args:
        problem_number: The Project Euler problem number.
    """
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
@register(name='backup',
          help='Back up problem files from the stack to the "backup" folder (unencrypted).',
          usage='backup')
def backup_the_stack() -> None:
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
        for problem_number in range(1, problems[-1].number + 1):
            config.workspace_dir = config.backup_dir / stack_base_dir(problem_number).relative_to(config.solutions_dir)
            unstack(problem_number)
            console.print(f'[muted]Stack backup for problem [accent]{problem_number}[/accent] → '
                          f'{canonical_path(config.workspace_dir)}[/muted]')
    finally:
        config.workspace_dir = orig_workspace_dir


@register(name='restore',
          help='Restore problem files from the "backup" folder to the stack (encrypted).',
          usage='restore')
def restore_the_stack() -> None:
    """
    Restore problem files from the 'backup' folder (unencrypted) to the stack (encrypted).
    Inverse of 'backup_the_stack'.
    """
    if not confirm('Are you sure, you want to restore the stack?'):
        console.print('[muted]Stack restoration cancelled.[/muted]')
        return
    orig_workspace_dir = config.backup_dir
    try:
        for problem_number in range(1, problems[-1].number + 1):
            config.workspace_dir = config.backup_dir / stack_base_dir(problem_number).relative_to(config.solutions_dir)
            stack(problem_number)
            console.print(f'[muted]Stack restored for problem [accent]{problem_number}[/accent] ← '
                          f'{canonical_path(config.workspace_dir)}[/muted]')
    finally:
        config.workspace_dir = orig_workspace_dir


# ==================================================================================================================== #
#                                               misc
# ==================================================================================================================== #
def has_new_solutions(problem_number: int) -> bool:
    """
    Determines if there are new solutions for a given problem based on file modification
    times.

    This function checks if any solution files in the specified problem's directory
    have a modification time later than the modification time of the problem's
    statement file. If such a file exists, the function returns True.

    Parameters:
        problem_number (int): The identifier for the problem to check for new solutions.

    Returns:
        bool: True if any solution file is newer than the statement file, otherwise False.
    """
    problem_stack_dir: Path = stack_base_dir(problem_number)
    statement_file_m_time: float = (problem_stack_dir / config.statement_filename).stat().st_mtime
    new_solutions: list[Path] = []
    for solution_file in (f for f in problem_stack_dir.iterdir() if f.is_file()):
        file_name: str = solution_file.name.removesuffix('.enc')
        if file_name.split('.')[-1] in ('py', 'c'):
            if solution_file.stat().st_mtime > statement_file_m_time:
                new_solutions.append(solution_file)
    if new_solutions:
        console.print(f'[success]{len(new_solutions)} new solutions found for problem '
                      f'[accent]{problem_number}[/accent]: '
                      f'{", ".join(f.name for f in new_solutions)}[/success]')
        return True
    test_cases_file: Path = stack_path(problem_number, config.test_cases_filename)[1]
    results_file: Path = stack_path(problem_number, config.results_filename)[1]
    if (
            test_cases_file.exists() and
            test_cases_file.stat().st_mtime > statement_file_m_time and
            results_file.exists() and
            results_file.stat().st_mtime > statement_file_m_time
    ):
        console.print(f'[success]Updated test cases and results found for problem '
                      f'[accent]{problem_number}[/accent][/success]')
        return True
    console.print(f'[muted]No new solutions or test cases and results for problem '
                  f'[accent]{problem_number}[/accent][/muted]')
    return False


__all__ = (
    'backup_the_stack',
    'has_new_solutions',
    'read_stack_file',
    'restore_the_stack',
    'stack',
    'stack_base_dir',
    'stack_path',
    'unstack',
    'write_stack_file',
)

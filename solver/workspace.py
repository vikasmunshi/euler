#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Workspace management: initialise, stack, list, and clear problem workspaces."""
from __future__ import annotations

from hashlib import sha256
from itertools import chain
from os import X_OK, access
from pathlib import Path

from solver.config import ColorCodes
from solver.parser import problem_statement
from solver.problems import Problem
from solver.stack import read_stack_file, stack, stack_base_dir, stack_path, unstack
from solver.utils import canonical_path, iterdir_recursive, run_command, write_file


def clear_the_workspace(workspace_dir: Path, *, discard_changes: bool = False) -> None:
    """
    Clear the workspace by deleting all files and directories.

    If the workspace has un-stacked changes and discard_changes is False, the workspace will be stacked first.
    if discard_changes is True, the workspace will be cleared immediately without stacking.

    Args:
        workspace_dir:   Path to the workspace directory.
        discard_changes: If True, clear the workspace without stacking changes first.
                         If False (default), stack the workspace before clearing if it differs from the stack.
    """
    if (problem := Problem.from_workspace(workspace_dir)) is not None:
        if discard_changes is False:
            if list_the_workspace(workspace_dir):
                stack_the_workspace(workspace_dir)
            print(f'Clearing workspace for problem {problem}...')
        else:
            print(f'Clearing workspace without stacking changes for problem {problem}...')
        run_command(f'rm -rf {workspace_dir.as_posix()}/*', silent=True)
        print('Workspace cleared.')


def init_the_workspace(problem_number: int, /, *, workspace_dir: Path, force_refresh: bool = False) -> None:
    """
    Initialize the workspace for the specified problem number.

    If a workspace is already initialized for a different problem number, it will be cleared
    (stacked first to preserve changes) before initializing the new problem workspace.

    Args:
        workspace_dir:  Path to the workspace directory.
        problem_number: Problem number of the projecteuler problem to initialize in the workspace.
        force_refresh:  Whether to force a refresh of the projecteuler files if they are already cached.
                        Defaults to False.
    """
    if (problem := Problem.from_number(problem_number)) is None:
        raise ValueError(f'Problem {problem_number} not found in problems')
    current: Problem | None = Problem.from_workspace(workspace_dir)
    if current and current.number != problem.number:
        clear_the_workspace(workspace_dir)
        print(f'Initializing workspace for problem {problem}...')
    elif current and current.number == problem.number:
        print(f'Restoring stack files for problem {problem}...')
    else:
        print(f'Initializing workspace for problem {problem}...')
    stack_dir: Path = stack_base_dir(problem.number)
    if stack_dir.exists():
        unstack(problem.number, workspace_dir=workspace_dir)
    problem, problem_statement_files = problem_statement(problem.number, force_refresh=force_refresh)
    for filename, content in problem_statement_files.items():
        write_file(workspace_dir / filename, content)
    problem.to_workspace(workspace_dir)
    print(f'Workspace init complete for problem {problem}')
    list_the_workspace(workspace_dir)


def list_the_workspace(workspace_dir: Path) -> bool:
    """
    Generates a summary report of the current workspace, including information related to
    file modifications, new files, and deleted files, comparing the current workspace
    contents with the stack for a specific problem.

    Args:
        workspace_dir: Path to the workspace directory.

    Returns:
        bool: True if the workspace differs from the stack, False otherwise.
    """
    if (problem := Problem.from_workspace(workspace_dir)) is None:
        print('No workspace initialized. Use init to initialize the workspace')
        return False
    has_changes: bool = False
    print(msg := f'Workspace for problem {problem!s}:')
    print('=' * len(msg))
    stack_dir: Path = stack_base_dir(problem.number)
    stack_files: set[str] = set(f.removesuffix('.enc') for f in iterdir_recursive(stack_dir, rt='str'))
    workspace_files: set[str] = set(iterdir_recursive(workspace_dir, rt='str'))
    max_filename_length: int = max(len(f) for f in chain(stack_files, workspace_files)) + 11
    lines: list[str] = []
    for filename in sorted(workspace_files.intersection(stack_files)):
        filepath: Path = workspace_dir / filename
        workspace_file_is_executable: bool = access(filepath, X_OK)
        workspace_file_part: str = (
            f'{"★" if workspace_file_is_executable else "○"} '
            f'{canonical_path(filepath):<{max_filename_length}}'
        )
        workspace_file_content: bytes = filepath.read_bytes()
        workspace_file_content_hash: str = sha256(workspace_file_content).hexdigest()
        _, stack_file_path = stack_path(problem.number, filename)
        stack_file_content, stack_file_is_executable = read_stack_file(problem.number, filename)
        stack_file_content_hash: str = sha256(stack_file_content).hexdigest()
        is_modified: bool = workspace_file_content_hash != stack_file_content_hash
        stack_file_part: str = (
            f'{"★" if stack_file_is_executable else "○"} '
            f'{canonical_path(stack_file_path):<{max_filename_length}}'
        )
        status: str = f'{ColorCodes.RED}≠{ColorCodes.RESET}' if is_modified else '='
        line: str = f'{workspace_file_part}{status} {stack_file_part}'
        lines.append(line)
        if is_modified:
            has_changes = True
    for filename in sorted(workspace_files - stack_files):
        filepath = workspace_dir / filename
        workspace_file_is_executable = access(filepath, X_OK)
        workspace_file_part = (
            f'{"★" if workspace_file_is_executable else "○"} '
            f'{canonical_path(filepath):<{max_filename_length}}'
        )
        line = f'{workspace_file_part}{ColorCodes.RED}+{ColorCodes.RESET}'
        lines.append(line)
        has_changes = True
    for filename in sorted(stack_files - workspace_files):
        _, stack_file_path = stack_path(problem.number, filename)
        stack_file_is_executable = access(stack_file_path, X_OK)
        stack_file_part = (
            f'{"★" if stack_file_is_executable else "○"} '
            f'{canonical_path(stack_file_path):<{max_filename_length}}'
        )
        line = f'{" " * 2}{"":<{max_filename_length}}{ColorCodes.RED}-{ColorCodes.RESET} {stack_file_part}'
        lines.append(line)
        has_changes = True
    print('\n'.join(lines))
    return has_changes


def stack_the_workspace(workspace_dir: Path, *, process_deletions: bool = False) -> None:
    """
    Stack the workspace for the current problem, restoring from backup and updating the stack file.

    Args:
        workspace_dir: Path to the workspace directory.
        process_deletions: Whether to process deletions during stacking, defaults to False.
    """
    if (problem := Problem.from_workspace(workspace_dir)) is None:
        print('No workspace initialized. Use init to initialize the workspace')
        return
    print(f'Stacking workspace for problem {problem} ...')
    if process_deletions:
        print('Processing deletions...')
        stack_dir: Path = stack_base_dir(problem.number)
        for stack_filename in iterdir_recursive(stack_dir, rt='str'):
            ws_filename = stack_filename.removesuffix('.enc')
            if not (workspace_dir / ws_filename).exists():
                print(f'Deleting {ws_filename} from stack...')
                (stack_dir / stack_filename).unlink()
    stack(problem.number, workspace_dir=workspace_dir)
    print('Stacking complete')


__all__ = (
    'clear_the_workspace',
    'init_the_workspace',
    'list_the_workspace',
    'stack_the_workspace',
)

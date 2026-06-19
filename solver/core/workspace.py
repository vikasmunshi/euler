#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Workspace management: initialise, stack, list, and clear problem workspaces."""
from __future__ import annotations

__all__ = ['init', 'ls', 'reset', 'stack']

from datetime import datetime
from hashlib import sha256
from itertools import chain
from os import X_OK, access
from pathlib import Path
from shutil import rmtree
from subprocess import run

from solver.config import ExitCodes, config
from solver.core.checkout import requires_checkin
from solver.core.lock import check_workspace_lock_command
from solver.core.parser import problem_statement
from solver.core.problems import Problem
from solver.core.stack import read_stack_file, stack_base_dir, stack_path, stack_to_solutions, unstack_from_solutions
from solver.crypto.keys import get_master_key, get_user_key
from solver.shell import console, register
from solver.shell.variables import refresh_workspace_vars, variables
from solver.utils.linter import lint
from solver.utils.path_utils import canonical_path, iterdir_recursive, write_file


@register(help_text='Initialize the workspace for the given problem number.', quietable=True)
@refresh_workspace_vars
@check_workspace_lock_command
@requires_checkin
def init(problem_number: int, /, *, refresh: bool = False) -> int:
    """
    Initialize the workspace for the specified problem number.

    If a workspace is already initialized for a different problem number, it will be reset
    before initializing the new problem workspace.

    Args:
        problem_number: Problem number of the projecteuler problem to initialize in the workspace.
        refresh:        Whether to force a refresh of the projecteuler files if they are already cached.
                        Defaults to False.
    """
    if problem_number > 100:
        try:
            get_user_key()
        except (AssertionError, FileNotFoundError, ValueError):
            console.print("Aha! getting serious... "
                          "use the [accent]'user'[/accent] command first, "
                          "then the [accent]'publish keys'[/accent] command "
                          "...and wait for an update.")
            return ExitCodes.EXIT_ERROR
        try:
            get_master_key()
        except (AssertionError, FileNotFoundError, ValueError):
            console.print("Have you tried the command [accent]'sync'[/accent] to check for updates?\n"
                          "Rome was not built in a day!")
            return ExitCodes.EXIT_ERROR
    if (problem := Problem.from_number(problem_number)) is None:
        console.print(f'[error]Problem {problem_number} not found in problems[/error]')
        return ExitCodes.EXIT_ERROR
    current: Problem | None = variables.problem
    if current and current.number != problem.number:
        if reset() != ExitCodes.EXIT_OK:
            console.print('[error]error:[/error] workspace could not be reset, please reset it first ]')
            return ExitCodes.EXIT_ERROR
        console.print(f'[primary]Initializing workspace for [accent]{problem.as_title()}[/accent]...[/primary]')
    elif current and current.number == problem.number:
        console.print(f'[primary]Restoring stack files for [accent]{problem.as_title()}[/accent]...[/primary]')
    elif current_files := list(canonical_path(f) for f in config.workspace_dir.iterdir()):
        console.print('[error]error:[/error] workspace is not empty, please reset it first ]')
        console.print(f'[muted]workspace contents:[/muted] {current_files}')
        return ExitCodes.EXIT_ERROR
    else:
        console.print(f'[primary]Initializing workspace for [accent]{problem.as_title()}[/accent]...[/primary]')
    if stack_base_dir(problem.number).exists():
        unstack_from_solutions(problem.number)
    else:
        refresh = True
    if refresh:
        console.print(f'[primary]Init problem statement files [muted]{refresh=}[/muted]...[/primary]')
        problem.to_workspace()
        problem, problem_statement_files = problem_statement(problem.number, force_refresh=True)
        for filename, content in problem_statement_files.items():
            write_file(config.workspace_dir / filename, content)
    console.print(f'[success]Workspace init complete for [accent]{problem.as_title()}[/accent][/success]')
    return ExitCodes.EXIT_OK


@register(help_text='List current workspace, indicating changes against stack.', aliases=('list',))
def ls() -> int:
    """
    Generates a summary report of the current workspace, including information related to
    file modifications, new files, and deleted files, comparing the current workspace
    contents with the stack for a specific problem.

    Returns:
        bool: True if the workspace differs from the stack, False otherwise.
    """
    if (problem := variables.problem) is None:
        return ExitCodes.EXIT_OK
    console.print(f'[primary]Workspace for [accent]{problem.as_title()}[/accent]:[/primary]')
    stack_dir: Path = stack_base_dir(problem.number)
    stack_files: set[str] = set(f.removesuffix('.enc') for f in iterdir_recursive(stack_dir, rt='str'))
    workspace_files: set[str] = set(iterdir_recursive(config.workspace_dir, rt='str'))
    max_filename_length: int = max(len(f) for f in chain(stack_files, workspace_files)) + 11
    lines: list[tuple[float, str]] = []
    for filename in sorted(workspace_files.intersection(stack_files)):
        filepath: Path = config.workspace_dir / filename
        workspace_file_content: bytes = filepath.read_bytes()
        workspace_file_content_hash: str = sha256(workspace_file_content).hexdigest()
        _, stack_file_path = stack_path(problem.number, filename)
        stack_file_content, stack_file_is_executable, stack_file_mtime = read_stack_file(problem.number, filename)
        stack_file_content_hash: str = sha256(stack_file_content).hexdigest()
        is_modified: bool = workspace_file_content_hash != stack_file_content_hash
        mtime: float = filepath.stat().st_mtime if is_modified else stack_file_mtime
        timestamp_part: str = f'{datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')}'
        workspace_file_part: str = (
            f'{"★" if access(filepath, X_OK) else "○"} '
            f'{canonical_path(filepath):<{max_filename_length}}'
        )
        stack_file_part: str = (
            f'{"★" if stack_file_is_executable else "○"} '
            f'stack/{stack_file_path.name}'
        )
        status: str = '[error]≠[/error]' if is_modified else '='
        lines.append((
            stack_file_mtime,
            f'[text]{timestamp_part} {workspace_file_part}{status} {stack_file_part}[/text]'
        ))
    for filename in sorted(workspace_files - stack_files):
        filepath = config.workspace_dir / filename
        ws_file_mtime: float = filepath.stat().st_mtime
        timestamp_part = f'{datetime.fromtimestamp(ws_file_mtime).strftime('%Y-%m-%d %H:%M:%S')}'
        workspace_file_part = (
            f'{"★" if access(filepath, X_OK) else "○"} '
            f'{canonical_path(filepath):<{max_filename_length}}'
        )
        stackable_marker: str = '' if _is_not_stackable(filename) else '[error]+[/error]'
        lines.append((
            ws_file_mtime,
            f'[text]{timestamp_part} {workspace_file_part}{stackable_marker}[/text]'
        ))
    for filename in sorted(stack_files - workspace_files):
        _, stack_file_path = stack_path(problem.number, filename)
        stack_file_mtime = stack_file_path.stat().st_mtime
        stack_file_is_executable = access(stack_file_path, X_OK)
        timestamp_part = f'{datetime.fromtimestamp(stack_file_mtime).strftime('%Y-%m-%d %H:%M:%S')}'
        workspace_file_part = f'  {"":<{max_filename_length}}'
        stack_file_part = (
            f'{"★" if stack_file_is_executable else "○"} '
            f'stack/{stack_file_path.name}'
        )
        lines.append((
            stack_file_mtime,
            f'[dim]{timestamp_part} {workspace_file_part}[error]-[/error] {stack_file_part}[/dim]'
        ))
    console.print('\n'.join(line[1] for line in sorted(lines, key=lambda x: x[0])))
    if _workspace_is_stackable(problem.number, stack_files=stack_files, workspace_files=workspace_files):
        return ExitCodes.EXIT_ERROR
    return ExitCodes.EXIT_OK


@register(help_text='Clear the workspace, and, if required, stack first.', quietable=True)
@refresh_workspace_vars
@check_workspace_lock_command
@requires_checkin
def reset(*, discard_changes: bool = False) -> int:
    """
    Clear the workspace by deleting all files and directories.

    If the workspace has unstacked changes and discard_changes is False, the workspace will be stacked first
    if discard_changes is True, the workspace will be cleared immediately without stacking.

    Args:
        discard_changes: If True, clear the workspace without stacking changes first.
                         If False (default), stack the workspace before clearing if it differs from the stack.
    """
    if (problem := variables.problem) is not None:
        if not discard_changes:
            if _workspace_is_stackable(problem.number):
                if stack() != ExitCodes.EXIT_OK:
                    return ExitCodes.EXIT_ERROR
            console.print(f'[primary]Clearing workspace for [accent]{problem.as_title()}[/accent]...[/primary]')
        else:
            console.print(f'[warning]Discarding workspace for [accent]{problem.as_title()}[/accent]...[/warning]')
    for item in config.workspace_dir.iterdir():
        if item.is_dir():
            rmtree(item)
        else:
            item.unlink()
    console.print('[success]Workspace cleared.[/success]')
    return ExitCodes.EXIT_OK


@register(help_text='Propagate stackable workspace changes to the stack.', aliases=('save',), quietable=True)
@check_workspace_lock_command
def stack(*, process_deletions: bool = True) -> int:
    """
    Stack the current problem in the workspace to the stack directory.

    Args:
        process_deletions: Whether to process deletions during stacking, defaults to True.
    """
    if (problem := variables.problem) is None:
        return ExitCodes.EXIT_ERROR
    if lint(auto_fix=True) != ExitCodes.EXIT_OK:
        return ExitCodes.EXIT_ERROR
    console.print(f'[primary]Stacking workspace for [accent]{problem.as_title()}[/accent]...[/primary]')
    if process_deletions:
        console.print('[muted]Processing deletions...[/muted]')
        stack_dir: Path = stack_base_dir(problem.number)
        for stack_filename in iterdir_recursive(stack_dir, rt='str'):
            ws_filename = stack_filename.removesuffix('.enc')
            if not (config.workspace_dir / ws_filename).exists():
                (stack_dir / stack_filename).unlink()
                console.print(f'[muted]Deleted [accent]{ws_filename}[/accent] from {canonical_path(stack_dir)}[/muted]')
    for workspace_file in iterdir_recursive(config.workspace_dir, rt='path'):
        if _is_not_stackable(workspace_file.name):
            if workspace_file.is_file():
                workspace_file.unlink(missing_ok=True)
            else:
                rmtree(workspace_file, ignore_errors=True)
            console.print(f'[muted]Deleted [accent]{workspace_file.name}[/accent] from workspace.[/muted]')
    stack_to_solutions(problem.number)
    run(f'git add -A "{config.solutions_dir.name}"', shell=True, cwd=config.root_dir)
    console.print('[success]Stacking complete[/success]')
    return ExitCodes.EXIT_OK


# ==================================================================================================================== #
#                                               misc
# ==================================================================================================================== #
def _workspace_is_stackable(problem_number: int, *,
                            stack_files: set[str] | None = None,
                            workspace_files: set[str] | None = None,
                            ) -> bool:
    if stack_files is None:
        _stack_dir: Path = stack_base_dir(problem_number)
        _stack_files: set[str] = set(f.removesuffix('.enc') for f in iterdir_recursive(_stack_dir, rt='str'))
    else:
        _stack_files = stack_files
    if workspace_files is None:
        _workspace_files: set[str] = set(
            f for f in iterdir_recursive(config.workspace_dir, rt='str')
            if not (f.endswith('_c') or f.startswith('.') or f.startswith('_'))
        )
    else:
        _workspace_files = {f for f in workspace_files if not _is_not_stackable(f)}
    if _stack_files - _workspace_files:
        return True
    if _workspace_files - _stack_files:
        return True
    for filename in _workspace_files.intersection(_stack_files):
        workspace_file_content: bytes = (config.workspace_dir / filename).read_bytes()
        stack_file_content: bytes = read_stack_file(problem_number, filename)[0]
        is_modified: bool = workspace_file_content != stack_file_content
        if is_modified:
            return True
    return False


def _is_not_stackable(filename: str) -> bool:
    return filename.endswith('_c') or filename.startswith('.') or filename.startswith('_')

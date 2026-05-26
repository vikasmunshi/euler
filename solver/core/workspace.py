#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Workspace management: initialise, stack, list, and clear problem workspaces."""
from __future__ import annotations

from hashlib import sha256
from itertools import chain
from os import X_OK, access
from pathlib import Path
from shutil import rmtree
from subprocess import run
from typing import Literal

from solver.config import config
from solver.core.evaluate import evaluate
from solver.core.lock import check_workspace, check_workspace_lock
from solver.core.parser import problem_statement
from solver.core.problems import Problem
from solver.core.stack import read_stack_file, stack, stack_base_dir, stack_path, unstack
from solver.crypto.keys import get_master_key, get_user_key
from solver.shell import console, register
from solver.utils.path_utils import canonical_path, iterdir_recursive, write_file


@register(name='benchmark',
          help='Benchmark the problem currently in the workspace.',
          usage='benchmark [all|dev|main|extra ...=all] '
                '[disable_timeout=false] [lang=*|py|c=*] [runs=21] [solution=*] [reset=false]', )
@check_workspace
def benchmark_the_workspace(*categories: Literal['all', 'dev', 'main', 'extra'],
                            disable_timeout: bool = False,
                            lang: Literal['*', 'py', 'c'] = '*',
                            runs: int = 21,
                            solution: str = '*',
                            reset: bool = False, ) -> Literal['ok', 'nok']:
    """
    Benchmarks the workspace using specified parameters.

    Args:
        *categories:        Test case categories to include. Accepts 'dev', 'main', 'extra', or 'all'
                            (which expands to all three). Defaults to 'all' if omitted.
        disable_timeout:    If True, disables timeout for solution execution. Defaults to False.
                            If True, only one run will be performed for each solution.
        lang:               Language to evaluate. Accepts '*', 'py' or 'c'. Defaults to '*'.
        runs:               Number of times to run each solution per test case.
                            Defaults to 21.
        solution:           Specific solution to evaluate.
                            If provided, only this solution will be evaluated.
                            If None, all solutions will be evaluated. Defaults to None.
        reset:              If True, replace any existing persisted results with this run on a
                            clean completion. If the benchmark is interrupted, existing results
                            are preserved untouched. Defaults to False (results are merged with
                            existing records as a running average).
    """
    if not categories:
        categories = ('all',)
    if disable_timeout:
        runs = 1
    try:
        evaluate(*categories,
                 disable_timeout=disable_timeout,
                 lang=lang,
                 record=True,
                 reset=reset,
                 runs=runs,
                 show=False,
                 solution=solution)
    except KeyboardInterrupt:
        console.print('[muted]Benchmark interrupted by user.[/muted]')
        return 'nok'
    else:
        console.print('[success]Benchmark complete.[/success]')
        return 'ok'


@register(name='init',
          help='Initialize the workspace for the given problem number.',
          usage='init <problem_number> [reinit=false] [force_refresh=false]')
@check_workspace_lock
def init_the_workspace(problem_number: int,
                       /, *,
                       reinit: bool = False,
                       force_refresh: bool = False,
                       ) -> Literal['ok', 'nok']:
    """
    Initialize the workspace for the specified problem number.

    If a workspace is already initialized for a different problem number, it will be cleared
    (changes discarded) before initializing the new problem workspace.

    Args:
        problem_number: Problem number of the projecteuler problem to initialize in the workspace.
        reinit:         Whether to reinitialize problem statement files
                        Defaults to False, which will skip re-downloading the problem statement files.
        force_refresh:  Whether to force a refresh of the projecteuler files if they are already cached.
                        Defaults to False. Will set reinit to True if True.
    """
    if problem_number > 100:
        try:
            get_user_key()
        except (AssertionError, FileNotFoundError, ValueError):
            console.print("Aha! getting serious... "
                          "use the [accent]'user'[/accent] command first, "
                          "then the [accent]'publish keys'[/accent] command "
                          "...and wait for an update.")
            return 'nok'
        try:
            get_master_key()
        except (AssertionError, FileNotFoundError, ValueError):
            console.print("Have you tried the command [accent]'sync'[/accent] to check for updates?\n"
                          "Rome was not built in a day!")
            return 'nok'
    if (problem := Problem.from_number(problem_number)) is None:
        console.print(f'[error]Problem {problem_number} not found in problems[/error]')
        return 'nok'
    current: Problem | None = Problem.from_workspace()
    if current and current.number != problem.number:
        reset_the_workspace(discard_changes=True)
        console.print(f'[primary]Initializing workspace for [accent]{problem.as_title()}[/accent]...[/primary]')
    elif current and current.number == problem.number:
        console.print(f'[primary]Restoring stack files for [accent]{problem.as_title()}[/accent]...[/primary]')
    elif current_files := list(config.workspace_dir.iterdir()):
        console.print('[error]error:[/error] workspace is not empty, please reset it first ]')
        console.print(f'[muted]workspace contents:[/muted] {current_files}')
        return 'nok'
    else:
        console.print(f'[primary]Initializing workspace for [accent]{problem.as_title()}[/accent]...[/primary]')
    reinit = reinit or force_refresh
    if stack_base_dir(problem.number).exists():
        unstack(problem.number)
    else:
        reinit = True
    if reinit:
        console.print(f'[primary]Init problem statement files [muted]{force_refresh=}[/muted]...[/primary]')
        problem.to_workspace()
        problem, problem_statement_files = problem_statement(problem.number, force_refresh=force_refresh)
        for filename, content in problem_statement_files.items():
            write_file(config.workspace_dir / filename, content)
    console.print(f'[success]Workspace init complete for [accent]{problem.as_title()}[/accent][/success]')
    return 'ok'


@register(name='list',
          help='List the current workspace contents, indicating changes against the stack.',
          usage='list',
          aliases=('ls',))
def list_the_workspace() -> bool:
    """
    Generates a summary report of the current workspace, including information related to
    file modifications, new files, and deleted files, comparing the current workspace
    contents with the stack for a specific problem.

    Returns:
        bool: True if the workspace differs from the stack, False otherwise.
    """
    if (problem := Problem.from_workspace()) is None:
        console.print('[muted]Use [accent]init[/accent] to initialize the workspace first.[/muted]')
        return False
    has_changes: bool = False
    console.print(f'[primary]Workspace for [accent]{problem.as_title()}[/accent]:[/primary]')
    stack_dir: Path = stack_base_dir(problem.number)
    stack_files: set[str] = set(f.removesuffix('.enc') for f in iterdir_recursive(stack_dir, rt='str'))
    workspace_files: set[str] = set(iterdir_recursive(config.workspace_dir, rt='str'))
    max_filename_length: int = max(len(f) for f in chain(stack_files, workspace_files)) + 11
    lines: list[str] = []
    for filename in sorted(workspace_files.intersection(stack_files)):
        filepath: Path = config.workspace_dir / filename
        workspace_file_is_executable: bool = access(filepath, X_OK)
        workspace_file_part: str = (
            f'{"★" if workspace_file_is_executable else "○"} '
            f'{canonical_path(filepath):<{max_filename_length}}'
        )
        workspace_file_content: bytes = filepath.read_bytes()
        workspace_file_content_hash: str = sha256(workspace_file_content).hexdigest()
        _, stack_file_path = stack_path(problem.number, filename)
        stack_file_content, stack_file_is_executable, _ = read_stack_file(problem.number, filename)
        stack_file_content_hash: str = sha256(stack_file_content).hexdigest()
        is_modified: bool = workspace_file_content_hash != stack_file_content_hash
        stack_file_part: str = (
            f'{"★" if stack_file_is_executable else "○"} '
            f'{canonical_path(stack_file_path):<{max_filename_length}}'
        )
        status: str = '[error]≠[/error]' if is_modified else '='
        line: str = f'{workspace_file_part}{status} {stack_file_part}'
        lines.append(line)
        if is_modified:
            has_changes = True
    for filename in sorted(workspace_files - stack_files):
        filepath = config.workspace_dir / filename
        workspace_file_is_executable = access(filepath, X_OK)
        workspace_file_part = (
            f'{"★" if workspace_file_is_executable else "○"} '
            f'{canonical_path(filepath):<{max_filename_length}}'
        )
        line = f'{workspace_file_part}[error]+[/error]'
        lines.append(line)
        has_changes = True
    for filename in sorted(stack_files - workspace_files):
        _, stack_file_path = stack_path(problem.number, filename)
        stack_file_is_executable = access(stack_file_path, X_OK)
        stack_file_part = (
            f'{"★" if stack_file_is_executable else "○"} '
            f'{canonical_path(stack_file_path):<{max_filename_length}}'
        )
        line = f'{" " * 2}{"":<{max_filename_length}}[error]-[/error] {stack_file_part}'
        lines.append(line)
        has_changes = True
    console.print('\n'.join(lines))
    return has_changes


@register(name='reinit',
          help='Re-initialize the workspace for the current problem.',
          usage='reinit [force_refresh=false]')
@check_workspace_lock
def reinit_the_workspace(force_refresh: bool = False) -> Literal['ok', 'nok']:
    """
    Re-initialize the workspace for the current problem.

    Args:
        force_refresh: Whether to force a refresh of the projecteuler files if they are already cached.
    """
    if (problem := Problem.from_workspace()) is None:
        console.print('[muted]Use [accent]init[/accent] to initialize the workspace first.[/muted]')
        return 'nok'
    return init_the_workspace(problem.number, reinit=True, force_refresh=force_refresh)


@register(name='reset',
          help='Clear the workspace, optionally stacking changes first.',
          usage='reset [discard_changes=true]')
@check_workspace_lock
def reset_the_workspace(*, discard_changes: bool = False) -> None:
    """
    Clear the workspace by deleting all files and directories.

    If the workspace has unstacked changes and discard_changes is False, the workspace will be stacked first
    if discard_changes is True, the workspace will be cleared immediately without stacking.

    Args:
        discard_changes: If True, clear the workspace without stacking changes first.
                         If False (default), stack the workspace before clearing if it differs from the stack.
    """
    if (problem := Problem.from_workspace()) is not None:
        if not discard_changes:
            if list_the_workspace():
                stack_the_workspace()
            console.print(f'[primary]Clearing workspace for [accent]{problem.as_title()}[/accent]...[/primary]')
        else:
            console.print(f'[warning]Discarding workspace for [accent]{problem.as_title()}[/accent]...[/warning]')
    for item in config.workspace_dir.iterdir():
        if item.is_dir():
            rmtree(item)
        else:
            item.unlink()
    console.print('[success]Workspace cleared.[/success]')


@register(name='stack',
          help='Save the current workspace contents to the problem stack.',
          usage='stack [process_deletions=true]',
          aliases=('save',))
@check_workspace_lock
def stack_the_workspace(*, process_deletions: bool = True) -> Literal['ok', 'nok']:
    """
    Stack the current problem in the workspace to the stack directory.

    Args:
        process_deletions: Whether to process deletions during stacking, defaults to True.
    """
    if (problem := Problem.from_workspace()) is None:
        console.print('[muted]Use [accent]init[/accent] to initialize the workspace first.[/muted]')
        return 'nok'
    linter_check = run(f'{config.scripts.linter} {config.workspace_dir.name}', shell=True, cwd=config.root_dir)
    if linter_check.returncode != 0:
        console.print(f'[error]Linter check failed:[/error] {problem} rc={linter_check.returncode}')
        return 'nok'
    console.print(f'[primary]Stacking workspace for [accent]{problem.as_title()}[/accent]...[/primary]')
    if process_deletions:
        console.print('[muted]Processing deletions...[/muted]')
        stack_dir: Path = stack_base_dir(problem.number)
        for stack_filename in iterdir_recursive(stack_dir, rt='str'):
            ws_filename = stack_filename.removesuffix('.enc')
            if not (config.workspace_dir / ws_filename).exists():
                console.print(
                    f'[muted]Deleting [accent]{ws_filename}[/accent] from {canonical_path(stack_dir)}[/muted]')
                (stack_dir / stack_filename).unlink()
    for workspace_file in config.workspace_dir.iterdir():
        if workspace_file.name.startswith('.'):
            if workspace_file.is_file():
                workspace_file.unlink(missing_ok=True)
            else:
                rmtree(workspace_file, ignore_errors=True)
    stack(problem.number)
    run(f'git add -A "{config.solutions_dir.name}"', shell=True, cwd=config.root_dir)
    console.print('[success]Stacking complete[/success]')
    list_the_workspace()
    return 'ok'


# ==================================================================================================================== #
#                                               misc
# ==================================================================================================================== #
@check_workspace
def has_new_solutions() -> bool:
    """ """
    notes_file: Path = config.workspace_dir / config.notes_filename
    if not notes_file.exists():
        console.print('[muted]No notes found[/muted]')
        return True
    notes_file_m_time: float = notes_file.stat().st_mtime
    new_solutions: list[Path] = []
    for solution_file in (f for f in config.workspace_dir.iterdir() if f.is_file()):
        file_name: str = solution_file.name.removesuffix('.enc')
        if file_name.split('.')[-1] in ('py', 'c'):
            if solution_file.stat().st_mtime > notes_file_m_time:
                new_solutions.append(solution_file)
    if new_solutions:
        console.print(f'[success]{len(new_solutions)} new solutions found: '
                      f'{", ".join(f.name for f in new_solutions)}[/success]')
        return True
    test_cases_file: Path = config.workspace_dir / config.test_cases_filename
    results_file: Path = config.workspace_dir / config.results_filename
    if (
            test_cases_file.exists() and
            test_cases_file.stat().st_mtime > notes_file_m_time and
            results_file.exists() and
            results_file.stat().st_mtime > notes_file_m_time
    ):
        console.print('[success]Updated test cases and results found[/success]')
        return True
    console.print('[muted]No new solutions or test cases and results[/muted]')
    return False


__all__ = (
    'init_the_workspace',
    'list_the_workspace',
    'reinit_the_workspace',
    'reset_the_workspace',
    'stack_the_workspace',
    'has_new_solutions',
)

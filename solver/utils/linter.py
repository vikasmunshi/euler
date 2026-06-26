#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Utilities for linting code. """
from __future__ import annotations

__all__ = ['lint', 'lazy_import_fix_code']

from subprocess import DEVNULL, run
from typing import Callable

from solver.config import ExitCodes, config
from solver.core.problems import Problem
from solver.shell import console, register
from solver.shell.variables import variables
from solver.utils.path_utils import canonical_path, iterdir_recursive


@register(help_text='Lint the workspace, fix with autoflake + autopep8 + isort.', quietable=True)
def lint(auto_fix: bool = False) -> int:
    """Lint the workspace solution files, optionally auto-fixing them.

    Checks the current problem's solution files for style and quality issues
    (flake8, plus the configured checks). Reports any findings and reflects them
    in the exit code.

    Args:
        auto_fix:   When True, attempt to fix issues in place with autoflake
                    (remove unused imports/variables), autopep8 (style), and
                    isort (import order), then re-check. When False (default),
                    only report. Fails if the workspace holds no problem.
    """
    problem = variables.problem
    console.print(f'[accent]checking[/accent] {problem}')
    if _linter_check(problem):
        return ExitCodes.EXIT_OK
    if auto_fix:
        console.print(f'\n[accent]auto-fixing [/accent] {problem}')
        if _auto_fix(problem):
            console.print(f'\n[accent]rechecking[/accent] {problem}')
            return ExitCodes.EXIT_OK if _linter_check(problem) else ExitCodes.EXIT_ERROR
    return ExitCodes.EXIT_ERROR


def _linter_check(problem: Problem) -> bool:
    # When the shared console is quiet, send the check subprocess to /dev/null too —
    # it writes straight to the terminal (inherited fds), so console.quiet alone won't hush it.
    pipe = DEVNULL if console.quiet else None
    linter_check = run(f'{config.scripts.linter} {canonical_path(problem.solution_dir)}', shell=True,
                       cwd=config.root_dir, stdout=pipe, stderr=pipe)
    if linter_check.returncode != 0:
        console.print(f'[error]check failed:[/error] {problem} rc={linter_check.returncode}')
        return False
    console.print(f'[primary]check passed[/primary] {problem}\n')
    return True


def lazy_import_fix_code() -> Callable[[str], str] | None:
    try:
        import autoflake
        import autopep8
        import isort
    except ImportError as exc:
        console.print(f'[error]auto-fix needs the [accent]dev[/accent] dependency group '
                      f'({exc.name} is not installed) — run [accent]pip install -e ".\\[dev]"[/accent].[/error]')
        return None

    def fix_code(source: str) -> str:
        code = autoflake.fix_code(source, remove_all_unused_imports=True, remove_duplicate_keys=True)
        code = autopep8.fix_code(code, options={'max_line_length': config.max_line_length})
        code = isort.code(code, profile='black', line_length=config.max_line_length)
        return code

    return fix_code


def _auto_fix(problem: Problem) -> bool:
    """Auto-fix the workspace Python files with autoflake + autopep8 + isort, then re-check.

    Dev-group deps, imported on demand so the shell starts without the `dev` group installed.
    """
    if (fix_code := lazy_import_fix_code()) is None:
        return False

    py_files = [
        f for f in iterdir_recursive(problem.solution_dir, rt='path')
        if f.is_file() and f.suffix == '.py'
    ]
    fixed = False
    for py_file in sorted(py_files):
        source = py_file.read_text()
        code = fix_code(source)
        if code != source:
            py_file.write_text(code)
            console.print(f'[primary]auto-fixed[/primary] {py_file.name}')
            fixed = True
    if not fixed:
        console.print(f'[warning]no auto-fixable changes for[/warning] {problem}')
    return fixed

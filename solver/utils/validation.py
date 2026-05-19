#! /usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" """
from __future__ import annotations

from json import JSONDecodeError, loads
from pathlib import Path
from typing import Any

from solver.core.config import config
from solver.core.console import console, register
from solver.core.stack import stack_base_dir
from solver.utils.path_utils import iterdir_recursive

__all__ = ['validate_stack_files']


@register(name='validate',
          help='Validate the structure of the stack files.',
          usage='validate', )
def validate_stack_files() -> int:
    c_files: set[str] = set()
    py_files: set[str] = set()
    misplaced_files: set[str] = set()
    corrupted_test_cases: set[int] = set()
    missing_main_test_cases: set[int] = set()
    misplaced_resources: set[str] = set()
    missing_problem_html: set[int] = set()
    for problem_number in range(1, 101):
        stack_dir: Path = stack_base_dir(problem_number)
        if not (stack_dir / config.statement_filename).exists():
            missing_problem_html.add(problem_number)
        for file in iterdir_recursive(stack_dir, rt='path'):
            if file.name.endswith('_c'):
                misplaced_files.add(file.name)
                continue
            if file.suffix not in ('.c', '.py'):
                continue
            qualified_filename: str = file.relative_to(stack_dir).as_posix()
            if file.suffix == '.c':
                c_files.add(qualified_filename.removesuffix('.c'))
            elif file.suffix == '.py':
                py_files.add(qualified_filename.removesuffix('.py'))
            if file.name[:7] != f'p{problem_number:04d}_s':
                misplaced_files.add(qualified_filename)
        try:
            test_cases: list[dict[str, Any]] = loads((stack_dir / config.test_cases_filename).read_text())
            main_test_case: dict[str, Any] | None = next((tc for tc in test_cases if tc['category'] == 'main'), None)
            if main_test_case is None:
                missing_main_test_cases.add(problem_number)
        except FileNotFoundError:
            pass
        except JSONDecodeError:
            corrupted_test_cases.add(problem_number)
        if (resource_dir := stack_dir / config.resource_dirname).exists():
            for resource in resource_dir.iterdir():
                if resource.stem.split('_')[0] != f'{problem_number:04d}':
                    misplaced_resources.add(resource.as_posix())
    missing_c_files: set[str] = py_files - c_files
    extra_c_files: set[str] = c_files - py_files
    if corrupted_test_cases:
        console.print(f'[warning]{len(corrupted_test_cases)} corrupted test cases: '
                      f'{", ".join(map(str, sorted(corrupted_test_cases)))}[/warning]')
    if extra_c_files:
        console.print(f'[warning]Extra {len(extra_c_files)} C files: '
                      f'{", ".join(f"{f}.c" for f in sorted(extra_c_files))}[/warning]')
    if misplaced_files:
        console.print(f'[warning]Misplaced {len(misplaced_files)} files: '
                      f'{", ".join(sorted(misplaced_files))}[/warning]')
    if misplaced_resources:
        console.print(f'[warning]Misplaced {len(misplaced_resources)} resources:\n'
                      f'{chr(10).join(sorted(misplaced_resources))}[/warning]')
    if missing_c_files:
        console.print(f'[warning]Missing {len(missing_c_files)} C files: '
                      f'{", ".join(f"{f}.c" for f in sorted(missing_c_files))}[/warning]')
    if missing_main_test_cases:
        console.print(f'[warning]{len(missing_main_test_cases)} problems without main test cases: '
                      f'{", ".join(map(str, sorted(missing_main_test_cases)))}[/warning]')
    if missing_problem_html:
        console.print(f'[warning]Missing problem HTML for {len(missing_problem_html)} problems: '
                      f'{", ".join(map(str, sorted(missing_problem_html)))}[/warning]')
    errors: int = (
            len(corrupted_test_cases) +
            len(extra_c_files) +
            len(misplaced_files) +
            len(misplaced_resources) +
            len(missing_c_files) +
            len(missing_main_test_cases) +
            len(missing_problem_html)
    )
    if errors == 0:
        console.print('[success]No errors found.[/success]')
    return errors


if __name__ == '__main__':
    raise SystemExit(validate_stack_files())

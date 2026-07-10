#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The `new` command and solution-file formatting (black / isort / autoflake)."""
from __future__ import annotations

__all__ = ['new']

import os
from pathlib import Path

from solver.config import ExitCodes, config
from solver.core.problems import Problem
from solver.shell import console, register
from solver.templates.engine import Templates, get_template
from solver.utils.path_utils import write_file

new_test_case: bytes = (
    b'[\n'
    b'  {\n'
    b'    "category": "dev",\n'
    b'    "input": {\n'
    b'      "n": 1\n'
    b'    },\n'
    b'    "answer": null\n'
    b'  },\n'
    b'  {\n'
    b'    "category": "main",\n'
    b'    "input": {\n'
    b'      "n": 10\n'
    b'    },\n'
    b'    "answer": null\n'
    b'  },\n'
    b'  {\n'
    b'    "category": "extra",\n'
    b'    "input": {\n'
    b'      "n": 100\n'
    b'    },\n'
    b'    "answer": null\n'
    b'  }\n'
    b']'
)


@register(requires=('solutions:write',),
          help_text='Generate new solution/test-case file for a problem.', quietable=True)
def new(problem: Problem, py: bool = False, c: bool = False, tc: bool = False) -> int:
    """Generate new solution and/or test-case files for the problem.

    Solution files are named from the problem number and the next free solution
    index (e.g. "p0001_s0.py", "p0001_s1.py") and are created from the boilerplate
    template with the problem information substituted; Python files are made
    executable (mode 0o755).

    Args:
        problem:    The `problem` to create files for; defaults to the current problem.
        py: Create a Python solution file. Defaults to False.
        c:  Create a C solution file (one per existing Python solution lacking a
            matching ".c"). Defaults to False.
        tc: Create an empty test-cases file instead of solution files, unless one
            already exists. Defaults to False.

    With neither `py` nor `c` given (and `tc` False), both a Python and a C file
    are created.
    """
    if tc:
        if not (test_cases_file := problem.solution_dir / config.test_cases_filename).exists():
            write_file(test_cases_file, new_test_case, f'created empty {config.test_cases_filename}')
        else:
            console.print(f'[primary]{config.test_cases_filename} already exists[/primary]')
        return ExitCodes.EXIT_OK
    new_py, new_c = py or not (py or c), c or not (py or c)
    prefix: str = f'p{problem.number:04d}_s'
    if new_py:
        k: int = 0
        while (problem.solution_dir / f'{prefix}{k}.py').exists():
            k += 1
        prefix = f'{prefix}{k}'
        py_file: Path = problem.solution_dir / f'{prefix}.py'
        code: str = get_template(Templates.NEW_PY).substitute(problem=problem.as_title())
        write_file(py_file, code.encode(), 'created solution file from template')
        os.chmod(py_file, 0o755)
    if new_c:
        for py_file in problem.solution_dir.glob(f'{prefix}*.py'):
            c_file: Path = py_file.with_suffix('.c')
            if c_file.exists():
                continue
            code = get_template(Templates.NEW_C).substitute(problem=problem.as_title())
            write_file(c_file, code.encode(), 'created solution file from template')
    return ExitCodes.EXIT_OK

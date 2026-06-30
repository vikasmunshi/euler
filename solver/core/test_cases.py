#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Load test cases for evaluation"""
from __future__ import annotations

__all__ = ['TestCase', 'load_test_cases']

from dataclasses import dataclass, field
from json import JSONDecodeError, loads
from pathlib import Path
from typing import Any, Literal, cast

from solver.config import ExitCodes, config
from solver.core.problems import Problem
from solver.core.results import read_results
from solver.shell import console, register

color_map: dict[str, str] = {
    'dev': 'primary',
    'main': 'success',
    'extra': 'accent.dim',
}


@dataclass
class TestCase:
    category: Literal['dev', 'main', 'extra']
    input: dict[str, Any]
    answer: Any | None
    runs: int
    input_args: list[str] = field(init=False)
    input_args_str: str = field(init=False)

    def __post_init__(self) -> None:
        self.input_args = [str(v) for v in self.input.values()]
        self.input_args_str = ' '.join(self.input_args)


def _clamp(x: int, min_val: int, max_val: int) -> int:
    """Clamp *x* into the inclusive range [min_val, max_val]."""
    return max(min(x, max_val), min_val)


def load_test_cases(problem: Problem,
                    *categories: Literal['dev', 'main', 'extra'],
                    solutions: list[str],
                    runs: int | None,
                    ) -> list[TestCase]:
    """Load and filter the workspace problem's test cases, resolving a per-category run count.

    Reads the test-cases file, keeps only cases whose category is in *categories*,
    and assigns each surviving case a `runs` value. Prints an error and returns an
    empty list if the file is missing, malformed, or has no case in *categories*.

    Args:
        problem:        The problem to evaluate, used to locate the test-cases file.
        *categories:    Categories to include ('dev', 'main', 'extra').
        solutions:      Solution filenames being evaluated; used to scope the prior
                        timings consulted for the adaptive run count.
        runs:           Fixed run count for every category, or None to derive it
                        adaptively per category from previously recorded *correct*
                        results as `clamp(round(21 / slowest_prior_average), 1, 21)`
                        (1 when there is no prior timing).

    Returns:
        The selected `TestCase` objects, with `input_args_str` padded to a common
        width for aligned output.
    """
    test_cases_path: Path = problem.solution_dir / config.test_cases_filename
    try:
        filtered: list[dict[str, Any]] = loads(test_cases_path.read_text())
        assert filtered and isinstance(filtered, list), 'empty or invalid test cases file'
        filtered = [tc for tc in filtered if tc['category'] in categories]
        assert filtered
    except FileNotFoundError:
        console.print('[error]error:[/error] no test cases found, skipping evaluation')
        return []
    except AssertionError:
        console.print(f'[error]error:[/error] no test cases for categories: {categories}, skipping evaluation')
        return []
    except JSONDecodeError as err:
        console.print(f'[error]error:[/error] invalid test cases file, skipping evaluation {err=}')
        return []
    if runs is None:
        existing_results = read_results(problem=problem)
        category_runs: dict[str, int] = {
            category: _clamp(round(21 / max(r.average for r in results)), 1, 21)
            if (results := [r for r in existing_results
                            if r.category == category and r.verdict == 'correct' and r.solution in solutions])
            else 1
            for category in categories
        }
    else:
        category_runs = {category: runs for category in categories}
    test_cases_list: list[TestCase] = [
        TestCase(category=tc['category'], input=tc['input'], answer=tc['answer'], runs=category_runs[tc['category']])
        for tc in filtered
    ]
    len_input_args_str: int = max(len(tc.input_args_str) for tc in test_cases_list)
    for test_case in test_cases_list:
        test_case.input_args_str = f'{test_case.input_args_str:<{len_input_args_str}}'
    return test_cases_list


@register(help_text='list the test cases for the problem.')
def test_cases(problem: Problem, *categories: Literal['all', 'dev', 'main', 'extra']) -> int:
    """
    List the test cases for a given problem based on specified categories.

    Args:
        problem:            The `problem` to list test cases for. This is used to locate the test cases file.
        *categories:        Test case categories to include. Accepts 'dev', 'main', 'extra', or 'all'
                            (which expands to all three). Defaults to all three if omitted.

    Returns:
        int: Exit code indicating the completion status of the operation.
    """
    if not categories or 'all' in categories:
        eval_categories: list[Literal['dev', 'main', 'extra']] = ['dev', 'main', 'extra']
    else:
        eval_categories = cast(list[Literal['dev', 'main', 'extra']], list(categories))
    max_args_len: int = 0
    output: list[tuple[str, str, str, str]] = []  # style, category, args, answer
    for test_case in load_test_cases(problem, *eval_categories, solutions=[], runs=None):
        args = test_case.input_args_str
        if 'https' in args:
            args = ' '.join([arg.split('/')[-1] if arg.startswith('https') else arg for arg in args.split()])
        max_args_len = max(max_args_len, len(args))
        output.append((color_map[test_case.category], test_case.category, args, str(test_case.answer or '')))
    for style, category, args, answer in output:
        console.print(f'[{style}]{category:<6}: {args:<{max_args_len}}[accent] → [/accent]{answer}[/{style}]')
    return ExitCodes.EXIT_OK

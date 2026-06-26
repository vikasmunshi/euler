#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Load test cases for evaluation"""
from __future__ import annotations

__all__ = ['TestCase', 'load_test_cases']

from dataclasses import dataclass, field
from json import JSONDecodeError, loads
from pathlib import Path
from typing import Any, Literal

from solver.config import config
from solver.core.results import read_results
from solver.shell import console, variables


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


def load_test_cases(*categories: Literal['dev', 'main', 'extra'],
                    solutions: list[str],
                    runs: int | None,
                    ) -> list[TestCase]:
    """Load and filter the workspace problem's test cases, resolving a per-category run count.

    Reads the test-cases file, keeps only cases whose category is in *categories*,
    and assigns each surviving case a `runs` value. Prints an error and returns an
    empty list if the file is missing, malformed, or has no case in *categories*.

    Args:
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
    test_cases_path: Path = variables.problem.solution_dir / config.test_cases_filename
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
        existing_results = read_results()
        category_runs: dict[str, int] = {
            category: _clamp(round(21 / max(r.average for r in results)), 1, 21)
            if (results := [r for r in existing_results
                            if r.category == category and r.verdict == 'correct' and r.solution in solutions])
            else 1
            for category in categories
        }
    else:
        category_runs = {category: runs for category in categories}
    test_cases: list[TestCase] = [
        TestCase(category=tc['category'], input=tc['input'], answer=tc['answer'], runs=category_runs[tc['category']])
        for tc in filtered
    ]
    len_input_args_str: int = max(len(tc.input_args_str) for tc in test_cases)
    for test_case in test_cases:
        test_case.input_args_str = f'{test_case.input_args_str:<{len_input_args_str}}'
    return test_cases

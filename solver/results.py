#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Results: save and retrieve problem results."""
from __future__ import annotations

from json import JSONDecodeError, dumps, loads
from types import TracebackType

from solver.config import ColorCodes, results_filename, workspace_dir
from solver.stack import read_stack_file, write_stack_file
from solver.utils import canonical_path

color_map: dict[str, ColorCodes] = {
    'correct': ColorCodes.GREEN,
    'incorrect': ColorCodes.RED,
    'unknown': ColorCodes.BLUE,
    'error': ColorCodes.RED,
    'overflow': ColorCodes.YELLOW,
    'timeout': ColorCodes.YELLOW,
}


class ResultsCollector:
    __slots__ = ('__record', '__results',)
    __record: bool
    __results: list[dict[str, str | float]]

    def __init__(self, record: bool) -> None:
        self.__record = record
        self.__results = []

    def __enter__(self) -> ResultsCollector:
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None,
                 tb: TracebackType | None) -> None:
        if self.__record:
            write_results(self.__results, problem_number=0)
            print(f'Results written to {canonical_path(workspace_dir / results_filename)}')

    def record(self, *, category: str, solution: str, args: str, answer: str | None, verdict: str,
               elapsed: float, ) -> None:
        self.__results.append({'category': category, 'solution': solution, 'args': args.strip(), 'answer': answer or '',
                               'verdict': verdict, 'elapsed': elapsed, })
        print(f'{color_map.get(verdict, ColorCodes.RED)} {category:<6} {f"({verdict})":<11} [{elapsed:.3f}s] '
              f'{solution} {args} -> {answer or ""}{ColorCodes.RESET}')


def best_correct_main_result(problem_number: int = 0) -> dict[str, str | float] | None:
    results = [r for r in read_results(problem_number) if r['category'] == 'main' and r['verdict'] == 'correct']
    if not results:
        return None
    return min(results, key=lambda x: x['elapsed'])


def correct_main_results(problem_number: int = 0) -> list[dict[str, str | float]]:
    return [r for r in read_results(problem_number) if r['category'] == 'main' and r['verdict'] == 'correct']


def read_results(problem_number: int = 0) -> list[dict[str, str | float]]:
    """Read problem results from a JSON file."""
    results: list[dict[str, str | float]]
    try:
        if problem_number == 0:
            results = loads((workspace_dir / results_filename).read_bytes())
        else:
            results = loads(read_stack_file(problem_number, results_filename)[0])
    except (FileNotFoundError, JSONDecodeError):
        results = []
    return results


def write_results(results: list[dict[str, str | float]], problem_number: int = 0) -> None:
    """Write problem results to a JSON file."""
    if problem_number == 0:
        (workspace_dir / results_filename).write_text(dumps(results, indent=2))
    else:
        write_stack_file(problem_number, results_filename, dumps(results, indent=2).encode(), is_executable=False)


__all__ = (
    'ResultsCollector',
    'best_correct_main_result',
    'correct_main_results',
    'read_results',
    'write_results',
)

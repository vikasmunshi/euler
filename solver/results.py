#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Results: save and retrieve problem results."""
from __future__ import annotations

from contextlib import contextmanager
from csv import reader
from datetime import datetime
from functools import lru_cache
from json import JSONDecodeError, dumps, loads
from typing import Generator, NamedTuple, Protocol

from solver.config import ColorCodes, results_filename, solutions_history_file, workspace_dir
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


class Recorder(Protocol):
    def __call__(self, *, category: str, solution: str, args: str, answer: str | None,
                 verdict: str, elapsed: float) -> None: ...


class Result(NamedTuple):
    category: str
    solution: str
    args: str
    answer: str | None
    verdict: str
    elapsed: float

    def __str__(self) -> str:
        return (f'{color_map.get(self.verdict, ColorCodes.RED)} '
                f'{self.category:<6} {f"({self.verdict})":<11} [{self.elapsed:.3f}s] '
                f'{self.solution} {self.args} -> {self.answer or ""}{ColorCodes.RESET}')


def read_results(problem_number: int = 0) -> list[Result]:
    """Read problem results from a JSON file."""
    try:
        if problem_number == 0:
            results = loads((workspace_dir / results_filename).read_bytes())
        else:
            results = loads(read_stack_file(problem_number, results_filename)[0])
    except (FileNotFoundError, JSONDecodeError):
        results = []
    return [Result(**r) for r in results]


@contextmanager
def results_collector(record: bool) -> Generator[Recorder, None, None]:
    """Context manager that collects run results and optionally persists them on a clean exit from the with block."""
    results: list[Result] = []

    def recorder(*, category: str, solution: str, args: str, answer: str | None, verdict: str,
                 elapsed: float, ) -> None:
        result = Result(category=category, solution=solution, args=args.strip(), answer=answer, verdict=verdict,
                        elapsed=elapsed)
        results.append(result)
        print(str(result))

    yield recorder

    if record:
        write_results(results, problem_number=0)
        print(f'Results written to {canonical_path(workspace_dir / results_filename)}')
    return None


@lru_cache(maxsize=None)
def solutions_history() -> dict[int, str]:
    """Return a mapping of problem number -> solve date read from solutions_history_file.

    The CSV has no header; columns are: problem_number, title, date_with_time.
    The date field looks like "20 Sep 25 (12:48)"; only the date portion is kept.
    """
    history: dict[int, str] = {}
    try:
        with solutions_history_file.open(newline='') as f:
            for row in reader(f):
                problem_number, _, date_with_time = int(row[0]), row[1], row[2]
                date_str = date_with_time.split(' (')[0].strip()
                history[problem_number] = datetime.strptime(date_str, '%d %b %y').strftime('%Y-%m-%d')
    except FileNotFoundError:
        pass
    return history


def write_results(results: list[Result], problem_number: int = 0) -> None:
    """Write problem results to a JSON file."""
    results_str = dumps([r._asdict() for r in results], indent=2)
    if problem_number == 0:
        (workspace_dir / results_filename).write_text(results_str)
    else:
        write_stack_file(problem_number, results_filename, results_str.encode(), is_executable=False)


__all__ = (
    'Result',
    'read_results',
    'results_collector',
    'solutions_history',
    'write_results',
)

if __name__ == '__main__':
    print(solutions_history())

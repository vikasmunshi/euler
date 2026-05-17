#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Results: save and retrieve problem results."""
from __future__ import annotations

from contextlib import contextmanager
from json import JSONDecodeError, dumps, loads
from time import time
from typing import Any, Generator, NamedTuple, Protocol

from solver.core.config import Config
from solver.core.stack import read_stack_file, write_stack_file
from solver.utils.path_utils import canonical_path
from solver.utils.workspace import check_workspace_lock

color_map: dict[str, Config.ColorCodes] = {
    'correct': Config.ColorCodes.GREEN,
    'incorrect': Config.ColorCodes.RED,
    'unknown': Config.ColorCodes.BLUE,
    'error': Config.ColorCodes.RED,
    'overflow': Config.ColorCodes.YELLOW,
    'timeout': Config.ColorCodes.YELLOW,
}


class Recorder(Protocol):
    def __call__(self, *, category: str, solution: str, args: str, answer: Any | None,
                 verdict: str, elapsed: float, runs: int) -> None: ...


class FormattedResult(NamedTuple):
    category: str
    solution: str
    args: str
    answer: Any | None
    verdict: str
    average: float
    number_runs: int

    solution_href: str
    args_short: str
    filename: str
    lang: str


class Result(NamedTuple):
    category: str
    solution: str
    args: str
    answer: Any | None
    verdict: str
    average: float
    number_runs: int

    def __str__(self) -> str:
        return (f'{color_map.get(self.verdict, Config.ColorCodes.RED)} '
                f'{self.category:<6} {f"({self.verdict})":<11} '
                f'[{self.average:<3.9f}s {self.number_runs}] '
                f'{self.solution} {self.args} -> {self.answer or ""}{Config.ColorCodes.RESET}')

    def formatted(self) -> FormattedResult:
        sol = (f'<a href="{self.solution}" target="_blank" rel="noopener noreferrer" title="{self.solution}">'
               f'{self.solution}'
               f'</a>')
        args: str = self.args
        if 'https' in self.args:
            args = ' '.join([arg.split('/')[-1] if arg.startswith('https') else arg for arg in self.args.split()])
        filename, lang = self.solution[:-2], self.solution[-2:]
        filename, lang = filename.rstrip('.'), lang.lstrip('_')
        return FormattedResult(**self._asdict(), solution_href=sol, args_short=args, filename=filename, lang=lang)


def read_results(problem_number: int = 0) -> list[Result]:
    """Read problem results from a JSON file."""
    try:
        if problem_number == 0:
            raw = loads((Config.workspace_dir / Config.results_filename).read_bytes())
        else:
            raw = loads(read_stack_file(problem_number, Config.results_filename)[0])
    except (FileNotFoundError, JSONDecodeError):
        raw = []
    return [Result(**r) for r in raw]


@contextmanager
def results_collector(record: bool) -> Generator[Recorder, None, None]:
    """Context manager that collects run results and optionally persists them on a clean exit from the with block."""
    results: list[Result] = []

    def recorder(*, category: str, solution: str, args: str, answer: Any | None, verdict: str,
                 elapsed: float, runs: int) -> None:
        result = Result(category=category, solution=solution, args=args.strip(), answer=answer,
                        verdict=verdict, average=elapsed, number_runs=runs)
        results.append(result)
        print(str(result))

    yield recorder

    if record:
        write_results(results, problem_number=0)
        print(f'Results written to {canonical_path(Config.workspace_dir / Config.results_filename)}')
    return None


@check_workspace_lock
def write_results(results: list[Result], problem_number: int = 0) -> None:
    """Write problem results to a JSON file, updating running averages.

    Reads existing records first and uses them to maintain a cumulative average
    and run count per (category, solution, args, verdict) key.
    Persists average and number_runs in place of the raw elapsed time.
    """
    try:
        if problem_number == 0:
            existing_raw = loads((Config.workspace_dir / Config.results_filename).read_bytes())
        else:
            existing_raw = loads(read_stack_file(problem_number, Config.results_filename)[0])
    except (FileNotFoundError, JSONDecodeError):
        existing_raw = []

    incoming: dict[tuple[str, str, str, str], Result] = {(r.category, r.solution, r.args, r.verdict): r
                                                         for r in results if r.verdict in ('correct', 'timeout')}
    updated: list[dict] = []
    for r in existing_raw:
        if r['verdict'] not in ('correct', 'timeout'):
            continue
        key = (r['category'], r['solution'], r['args'], r['verdict'])
        if key in incoming:
            nr = incoming.pop(key)
            old_avg, old_n = r['average'], r['number_runs']
            new_avg = (old_avg * old_n + nr.average * nr.number_runs) / (old_n + nr.number_runs)
            d = nr._asdict()
            d['average'] = new_avg
            d['number_runs'] = old_n + nr.number_runs
            updated.append(d)
        else:
            updated.append(r)
    for r in incoming.values():
        updated.append(r._asdict())

    results_str = dumps(updated, indent=2)
    if problem_number == 0:
        (Config.workspace_dir / Config.results_filename).write_text(results_str)
    else:
        write_stack_file(
            problem_number,
            Config.results_filename,
            results_str.encode(),
            is_executable=False,
            m_time=time()
        )


__all__ = (
    'FormattedResult',
    'Result',
    'read_results',
    'results_collector',
    'write_results',
)

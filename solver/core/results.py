#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Results: save and retrieve problem results."""
from __future__ import annotations

__all__ = ['FormattedResult', 'Result', 'read_results', 'results_collector', 'write_results']

from contextlib import contextmanager
from json import JSONDecodeError, dumps, loads
from typing import Any, Generator, Literal, NamedTuple, Protocol, cast

from solver.config import ExitCodes, config
from solver.core.problems import Problem
from solver.shell import console, register
from solver.utils.path_utils import write_file

color_map: dict[str, str] = {
    'correct': 'success',
    'incorrect': 'error',
    'unknown': 'primary',
    'error': 'error',
    'overflow': 'warning',
    'timeout': 'warning',
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
        """Render the result as a single rich-markup line, coloured by verdict.

        URL arguments are abbreviated to their final path segment for brevity.
        """
        style = color_map.get(self.verdict, 'error')
        args: str = self.args
        if 'https' in self.args:
            args = ' '.join([arg.split('/')[-1] if arg.startswith('https') else arg for arg in self.args.split()])
        return (f'[muted]{self.category:<6} [{style}]{f"({self.verdict})":<13}[/{style}]'
                f' \\[{self.average:<3.9f}s {self.number_runs}] {self.solution} {args}[/muted]'
                f'[accent] → [/accent]'
                f'[{style}]{str(self.answer or "")}[/{style}]')

    def formatted(self) -> FormattedResult:
        """Return a `FormattedResult` enriched for HTML display.

        Adds an anchor-tag link to the solution, an abbreviated args string (URLs
        reduced to their final segment), and the solution split into its base
        filename and language suffix.
        """
        sol = (f'<a href="{self.solution}" target="_blank" rel="noopener noreferrer" title="{self.solution}">'
               f'{self.solution}'
               f'</a>')
        args: str = self.args
        if 'https' in self.args:
            args = ' '.join([arg.split('/')[-1] if arg.startswith('https') else arg for arg in self.args.split()])
        filename, lang = self.solution[:-2], self.solution[-2:]
        filename, lang = filename.rstrip('.'), lang.lstrip('_')
        return FormattedResult(**self._asdict(), solution_href=sol, args_short=args, filename=filename, lang=lang)


def read_results(problem: Problem) -> list[Result]:
    """Read problem results from a JSON file."""
    try:
        raw = loads((problem.solution_dir / config.results_filename).read_bytes())
    except (FileNotFoundError, JSONDecodeError):
        raw = []
    return [Result(**r) for r in raw]


@contextmanager
def results_collector(problem: Problem, record: bool, reset: bool = False) -> Generator[Recorder, None, None]:
    """Context manager that collects run results and persists them on exit.

    Persistence is controlled by "record" and "reset":

    * record=False                       — never write; results are discarded on exit.
    * record=True,  reset=False, clean   — merge new results into the existing file.
    * record=True,  reset=False, abort   — merge partial results into the existing file
                                           (interrupted runs still contribute what they
                                           managed to collect).
    * record=True,  reset=True,  clean   — replace the existing file with the new run.
    * record=True,  reset=True,  abort   — skip writing entirely, leaving the existing
                                           file untouched (a partial reset would be a
                                           silent destructive overwrite).
    """
    results: list[Result] = []

    def recorder(*, category: str, solution: str, args: str, answer: Any | None, verdict: str,
                 elapsed: float, runs: int) -> None:
        result = Result(category=category, solution=solution, args=args.strip(), answer=answer,
                        verdict=verdict, average=elapsed, number_runs=runs)
        results.append(result)
        console.print(str(result))

    clean_exit: bool = False
    try:
        yield recorder
        clean_exit = True
    finally:
        if record and (clean_exit or not reset):
            write_results(problem=problem, results=results, reset=reset and clean_exit)


def write_results(problem: Problem, results: list[Result], reset: bool = False) -> None:
    """Write problem results to a JSON file.

    By default (reset=False) existing records are read first and merged with the
    incoming results: matching (category, solution, args, verdict) keys have their
    average and run count rolled into a running average, and non-matching existing
    entries are preserved.

    When reset=True the existing file is ignored and the persisted file is replaced
    by the incoming results only. The caller is expected to gate this on a clean
    completion of the evaluation (see "results_collector") so a partial run cannot
    silently overwrite previously good data.

    By design only stable verdicts are persisted: incoming results are kept when
    their verdict is in ('correct', 'timeout', 'overflow'), while existing records
    are retained (on a non-reset rewrite) only when their verdict is in
    ('correct', 'timeout'). The remaining transient verdicts ('incorrect',
    'error', 'unknown') are intentionally discarded so the persisted file
    represents the stable benchmark surface.

    Args:
        problem:        The problem under evaluation, used to locate the `results` file.
        results:        Results collected during the run.
        reset:          If True, ignore existing records and replace the file with
                        "results" only. Defaults to False.
    """
    if reset:
        existing_raw: list[dict[str, Any]] = []
    else:
        try:
            existing_raw = loads((problem.solution_dir / config.results_filename).read_bytes())
        except (FileNotFoundError, JSONDecodeError):
            existing_raw = []

    incoming: dict[tuple[str, str, str, str], Result] = {(r.category, r.solution, r.args, r.verdict): r
                                                         for r in results
                                                         if r.verdict in ('correct', 'timeout', 'overflow')}
    updated: list[dict] = []
    for existing in existing_raw:
        if existing['verdict'] not in ('correct', 'timeout'):
            continue
        key = (existing['category'], existing['solution'], existing['args'], existing['verdict'])
        if key in incoming:
            nr = incoming.pop(key)
            old_avg, old_n = existing['average'], existing['number_runs']
            new_avg = (old_avg * old_n + nr.average * nr.number_runs) / (old_n + nr.number_runs)
            d = nr._asdict()
            d['average'] = new_avg
            d['number_runs'] = old_n + nr.number_runs
            updated.append(d)
        else:
            updated.append(existing)
    for incoming_result in incoming.values():
        updated.append(incoming_result._asdict())

    write_file(problem.solution_dir / config.results_filename, dumps(updated, indent=2).encode(),
               'Updated results')


@register(help_text='list the results for the problem.')
def results(problem: Problem, *categories: Literal['all', 'dev', 'main', 'extra']) -> int:
    """List the results for a given problem.
    Args:
        problem:            The `problem` to list `results` for. This is used to locate the `results` file.
        *categories:        Test case categories to include. Accepts 'dev', 'main', 'extra', or 'all'
                            (which expands to all three). Defaults to all three if omitted.

    Returns:
        int: Exit code indicating the completion status of the operation.
    """
    if not categories or 'all' in categories:
        eval_categories: list[Literal['dev', 'main', 'extra']] = ['dev', 'main', 'extra']
    else:
        eval_categories = cast(list[Literal['dev', 'main', 'extra']], list(categories))
    _results = read_results(problem)
    if not _results:
        console.print('[error]error:[/error] no results found, skipping display')
        return ExitCodes.EXIT_NOTFOUND
    console.print('\n'.join(str(r) for r in _results if r.category in eval_categories))
    return ExitCodes.EXIT_OK

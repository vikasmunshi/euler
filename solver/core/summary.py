#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The `summary`, `progress` and `mark` commands: the shell's side of `problems.json`.

The parsing and the solved-preserving merge are shared with the web tier's progress upload
and live in :mod:`solver.core.progress`; this module adds what only the shell has — the
config-resolved paths, the console, the staff notice, and fetching new problems.
"""
from __future__ import annotations

__all__ = ['summary', 'mark', 'progress']

from datetime import datetime
from json import JSONDecodeError, loads
from pathlib import Path
from typing import Any

from solver.config import ExitCodes, config
from solver.core import osc
from solver.core.git import commit_regenerated
from solver.core.problems import Problem, format_solved_date, problems
from solver.core.progress import ProblemRecord, merge_progress, parse_progress
from solver.shell import console, register
from solver.utils.path_utils import canonical_path
from solver.utils.quips import quips
from solver.web.msg import UNREGISTERED_SUBJECT


def _parse_progress_html() -> dict[int, ProblemRecord]:
    """Parse `.progress.html` (see :func:`solver.core.progress.parse_progress`); `{}` when absent."""
    progress_file = config.static_file_progress
    if not progress_file.exists():
        return {}
    return parse_progress(progress_file.read_text(encoding='utf-8', errors='replace'))


def _report_unregistered(numbers: list[int]) -> None:
    """Say — on the console, and to staff — which solved answers the progress page lacks.

    Best-effort on the message, like every other :mod:`solver.web.msg.notify` caller: the
    state is already written and correct, so a spool that is down or absent costs a nudge and
    nothing else. The console line is printed either way, since the person who just ran
    `summary` is the one who can go and register the answer.
    """
    from solver.web.msg.notify import notify_staff
    listed: str = ', '.join(str(number) for number in numbers)
    what: str = f'problem {listed}' if len(numbers) == 1 else f'{len(numbers)} problems'
    if len(numbers) == 1:
        console.print(f'[warning]answer for problem {listed} not registered on '
                      'projecteuler.net[/warning]')
    else:
        console.print(f'[warning]answer not registered on projecteuler.net for '
                      f'{len(numbers)} problems: {listed}[/warning]')
    notify_staff(
        f'{UNREGISTERED_SUBJECT}{what}',
        'These problems are recorded as solved, but the progress page does not show them as '
        'solved — so the answer was never registered on projecteuler.net:\n\n'
        + ''.join(f'    answer for problem {number} not registered\n' for number in numbers)
        + '\nThe recorded state has been kept as it was. Submit each answer on '
          'https://projecteuler.net, then run `summary` again.\n')


def _update_problems_state(_problems: dict[int, ProblemRecord]) -> None:
    """Update the on-disk and in-memory problems state from parsed problem metadata.

    The write is a merge, not a replacement (:func:`solver.core.progress.merge_progress`),
    so a re-imported progress page can add solved problems but never take one away.
    Disagreements — solved here, not solved on the page — are reported
    (:func:`_report_unregistered`).

    Args:
        _problems: Dictionary mapping problem numbers to their metadata
                  (title, level, pct, solved, date).
    """
    unregistered: list[int] = merge_progress(config.static_file_problems, _problems)
    problems.clear_cache()
    osc.progress_changed()   # a web upload's grid is waiting on this (solver.web.site.app.progress_save)
    if unregistered:
        _report_unregistered(unregistered)


@register(requires='maintainer', quietable=True)
def summary() -> int:
    """Refresh the solved/unsolved state from your Project Euler progress page.

    Parses `solutions/.progress.html` (the saved Page Source of your
    authenticated https://projecteuler.net/progress page) and updates
    `problems.json` with which problems are solved and their metadata. This is
    how the shell learns your real progress, driving `{solved}` / `{unsolved}`,
    `progress`, and `solved`.

    It is also where new problems arrive: each problem the page lists that has no
    solution directory yet gets its statement and resources downloaded. A failed
    download fails the command once the rest are done; re-running retries it.

    What it wrote is committed — `problems.json` and each new problem's statement,
    `__init__.py` and resources, and nothing beside them — so new problems reach other
    clones by `git-sync` instead of every clone fetching its own copy.

    The import only ever **adds** solved problems: a problem `mark` recorded as solved
    keeps that record, and its date, even when the page does not show it as solved —
    which is the normal state of a problem solved here but whose answer has not been
    registered on projecteuler.net yet. Each such disagreement is reported, and staff
    are sent a message naming the problems.

    Returns an error (with instructions) if `.progress.html` is missing: visit
    the progress page, copy its Page Source into that file, and retry.
    """
    _problems = _parse_progress_html()
    if not _problems:
        tab: str = ' ' * len('error: ')
        target_file: str = canonical_path(config.static_file_progress)
        console.print('[error]error:[/error] '
                      '[muted]'
                      f'{target_file} not found.\n'
                      f'{tab}Summary generation aborted.\n'
                      f'{tab}Instructions to create the file:\n'
                      f'{tab}Visit https://projecteuler.net/progress (requires authentication)\n'
                      f'{tab}Copy the \'Page Source\' into the file {target_file} and retry.'
                      '[/muted]')
        return ExitCodes.EXIT_ERROR
    _update_problems_state(_problems)
    fetched, failed = _fetch_new_problems()
    written: list[str] = [_relative(config.static_file_problems), *(_relative(path) for path in fetched)]
    new: list[str] = sorted({_relative(path.parent) for path in fetched if path.name == config.statement_filename})
    committed: int = commit_regenerated('summary', quips['summary'], written,
                                        [f'new problem: {name}' for name in new])
    return int(ExitCodes.EXIT_ERROR) if failed else committed


def _relative(path: Path) -> str:
    """*path* as the repo-relative POSIX name `commit_regenerated` takes."""
    return path.relative_to(config.root_dir).as_posix()


def _fetch_new_problems() -> tuple[list[Path], int]:
    """Download the statement of every problem `problems.json` knows but the stack lacks.

    This is the one place new problems are discovered, so it is the one place they are
    fetched — no longer as a side effect of the first lookup, which made every clone fetch
    on its first run and then collide with the same files arriving by `git-sync`.

    Returns every file written (for :func:`summary` to commit) and how many problems
    failed. Each failure is reported and the rest carry on; running `summary` again
    retries exactly those, since their directories are still missing.
    """
    fetched: list[Path] = []
    failed: int = 0
    for problem in problems.missing_problems:
        console.print(f'[muted]fetching statement for {problem}[/muted]')
        try:
            fetched.extend(problem.init())
        except ValueError as exc:
            console.print(f'[error]error:[/error] {exc}')
            failed += 1
    if failed:
        console.print(f'[warning]{failed} statement(s) could not be fetched — run '
                      '[accent]summary[/accent] again to retry.[/warning]')
    return fetched, failed


@register(requires='reader')
def progress() -> int:
    """Print overall progress through the Euler problems.

    Shows a bar of solved vs. unsolved problems, the solved count and
    percentage of the total known problems, and the next problem to solve (the
    lowest-numbered unsolved one). Reads the state maintained by `summary`; run
    `summary` first if your progress looks out of date.
    """
    problems.clear_cache()
    total: int = len(problems.problems_list)
    solved: int = len(problems.solved_problems)
    next_to_solve: Problem = next((problem for problem in problems.problems_list
                                   if problem not in problems.solved_problems), problems.problems_list[-1])
    # Calculate bar widths (max 50 characters total)
    bar_width: int = 50
    solved_width: int = int((solved / total) * bar_width)
    unsolved_width: int = bar_width - solved_width
    # Create the bar
    solved_bar = '█' * solved_width
    unsolved_bar = '░' * unsolved_width
    console.print(
        f'\n[green]{solved_bar}[/green][dim]{unsolved_bar}[/dim]\n'
        f'[muted]{"Progress:":>18} {solved}/{total} ({(solved / total * 100) if total > 0 else 0:.1f}%)[/muted]'
        f'\n[muted]{"Next to solve:":>18} {next_to_solve}[/muted]\n'
    )
    return ExitCodes.EXIT_OK


@register(requires='contributor', aliases=('mark-solved',), quietable=True)
def mark(problem: Problem) -> int:
    """Mark the current problem as solved — once its results confirm it.

    Records the current problem as solved (with today's date) in
    `problems.json`, the same state `summary` maintains, so `{solved}`,
    `progress`, and `solved` reflect it without re-importing the progress page.

    It only proceeds after checking the recorded results: there must be a
    selected problem, its `test_cases.json` must have a `main` case with an
    answer, and `results.json` must contain a `correct` verdict for that `main`
    case. Run `benchmark` (which records results) first; a problem already
    marked solved is left unchanged.

    Aliased as `mark-solved`.

    Args:
        problem: [problem] The problem to mark solved.
    """
    _problems: dict[int, ProblemRecord] = {
        int(k): v
        for k, v in loads(config.static_file_problems.read_text()).items()
    }
    if _problems[problem.number]['solved']:
        console.print(f'[muted]Problem {problem.number} is already marked as solved.[/muted]')
        return ExitCodes.EXIT_OK
    try:
        test_cases: list[dict[str, Any]] = loads((problem.solution_dir / config.test_cases_filename).read_text())
    except FileNotFoundError:
        console.print(f'[error]error:[/error] [muted]Test cases file not found for {problem}[/muted]')
        return ExitCodes.EXIT_ERROR
    except JSONDecodeError:
        console.print(f'[error]error:[/error] [muted]Failed to parse test cases for {problem}[/muted]')
        return ExitCodes.EXIT_ERROR
    main_test_case = next((tc for tc in test_cases if tc['category'] == 'main'), None)
    if main_test_case is None or main_test_case['answer'] is None:
        console.print(f'[error]error:[/error] [muted]{problem} is not solved.[/muted]')
        return ExitCodes.EXIT_ERROR
    try:
        results: list[dict[str, Any]] = loads((problem.solution_dir / config.results_filename).read_text())
    except FileNotFoundError:
        console.print(f'[error]error:[/error] [muted]Results file not found for {problem}[/muted]')
        return ExitCodes.EXIT_ERROR
    except JSONDecodeError:
        console.print(f'[error]error:[/error] [muted]Failed to parse results for {problem}[/muted]')
        return ExitCodes.EXIT_ERROR
    correct: list[dict[str, Any]] = [r for r in results if r['verdict'] == 'correct' and r['category'] == 'main']
    if not correct:
        console.print(f'[error]error:[/error] [muted]{problem} is not solved.[/muted]')
        return ExitCodes.EXIT_ERROR
    _problems[problem.number]['solved'] = True
    _problems[problem.number]['date'] = format_solved_date(datetime.now())
    _update_problems_state(_problems)
    return ExitCodes.EXIT_OK


if __name__ == '__main__':
    summary()

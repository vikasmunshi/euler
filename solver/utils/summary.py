#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Progress: parse .progress.html into problems.json and refresh in-memory state."""
from __future__ import annotations

__all__ = ['summary', 'mark', 'progress']

from datetime import datetime
from json import JSONDecodeError, dumps, loads
from typing import Any

from bs4 import BeautifulSoup, Tag

from solver.config import ExitCodes, config
from solver.core.problems import Problem, problems
from solver.shell import console, register
from solver.utils.path_utils import canonical_path
from solver.web.msg import UNREGISTERED_SUBJECT


def _parse_progress_html() -> dict[int, dict[str, str | int | bool]]:
    """Parse .progress.html and return problem metadata.

    Returns dict mapping problem_number -> {title, level, pct, solved, date}.
    level and pct are ints or '' when unknown; date is '' for unsolved problems.
    """
    progress_file = config.static_file_progress
    if not progress_file.exists():
        return {}
    soup: BeautifulSoup = BeautifulSoup(progress_file.read_text(encoding='utf-8', errors='replace'), 'html.parser')
    _problems: dict[int, dict[str, str | int | bool]] = {}
    for td in soup.find_all('td', class_='tooltip'):
        a_tag = td.find('a', href=True)
        if not a_tag or not str(a_tag.get('href', '')).startswith('problem='):
            continue
        try:
            num = int(str(a_tag['href']).split('=')[1])
        except (ValueError, IndexError):
            continue
        # Difficulty level from CSS class t_N
        level: int | str = ''
        for cls in (td.get('class') or []):
            if cls.startswith('t_'):
                try:
                    level = int(cls[2:])
                except ValueError:
                    pass
        # Title, percentage, and completion date from tooltip span
        title: str = ''
        pct: int | str = ''
        date: str = ''
        tooltip: Tag | None = a_tag.find('span', class_='tooltiptext_narrow')
        if tooltip:
            for div in tooltip.find_all('div'):
                text: str = div.get_text(strip=True)
                if text.startswith('"') and text.endswith('"'):
                    title = text[1:-1]
                elif 'Difficulty:' in text and '[' in text:
                    try:
                        pct = int(text.split('[')[1].split('%')[0].strip())
                        if level == '' and 'Level' in text:
                            level = int(text.split('Level')[1].split('[')[0].strip())
                    except (ValueError, IndexError):
                        pass
                elif text.startswith('Completed on '):
                    date = text[len('Completed on '):]
        solved: bool = 'problem_solved' in (td.get('class') or [])
        _problems[num] = {'title': title, 'level': level, 'pct': pct, 'solved': solved, 'date': date}
    return _problems


def _recorded_problems() -> dict[int, dict[str, str | int | bool]]:
    """The problems file as it stands now, keyed by number — `{}` when it cannot be read.

    A missing or unparsable file is not an error here: the first `summary` on a fresh clone
    has nothing to compare against, and the write that follows is what creates it. Anything
    unreadable is treated as "nothing recorded" rather than refused, since the parsed page is
    the better of the two states either way.
    """
    try:
        raw: Any = loads(config.static_file_problems.read_text())
    except (OSError, JSONDecodeError):
        return {}
    if not isinstance(raw, dict):
        return {}
    recorded: dict[int, dict[str, str | int | bool]] = {}
    for key, value in raw.items():
        try:
            number = int(key)
        except (TypeError, ValueError):
            continue
        if isinstance(value, dict):
            recorded[number] = value
    return recorded


def _carry_solved(_problems: dict[int, dict[str, str | int | bool]],
                  recorded: dict[int, dict[str, str | int | bool]]) -> list[int]:
    """Keep every `solved` record *recorded* already holds; return the numbers the page denies.

    `solved` is written from two directions and only one of them is the progress page: `mark`
    sets it the moment a problem's own `results.json` confirms the answer, which is *before*
    the answer has been given to projecteuler.net (sometimes long before). A re-import that
    simply overwrote the file would silently un-solve all of those, taking their dates with
    them — so the merge is one-way: a solved record survives a page that does not carry it,
    with its original date, and nothing here ever clears a `solved` flag.

    The numbers returned are exactly the disagreements: solved in the file, not solved on the
    page. Each one means the same thing — the answer was never registered upstream — which is
    worth telling somebody about, because it is the half of solving a problem that the solver
    cannot do for you.
    """
    unregistered: list[int] = []
    for number, was in sorted(recorded.items()):
        if not was.get('solved'):
            continue
        current = _problems.get(number)
        if current is None:
            # The page does not carry this problem at all (a partial save, or a problem
            # withdrawn upstream). Carry the whole record over rather than drop a solution.
            _problems[number] = dict(was)
        elif not current.get('solved'):
            current['solved'] = True
            current['date'] = was.get('date') or current.get('date', '')
        else:
            continue
        unregistered.append(number)
    return unregistered


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


def _update_problems_state(_problems: dict[int, dict[str, str | int | bool]]) -> None:
    """Update the on-disk and in-memory problems state from parsed problem metadata.

    The write is a merge, not a replacement: :func:`_carry_solved` folds the solved records
    the file already holds into *_problems* first, so a re-imported progress page can add
    solved problems but never take one away. Disagreements — solved here, not solved on the
    page — are reported (:func:`_report_unregistered`).

    Args:
        _problems: Dictionary mapping problem numbers to their metadata
                  (title, level, pct, solved, date).
    """
    unregistered: list[int] = _carry_solved(_problems, _recorded_problems())
    # By number, so a record carried over from the old file lands where it belongs rather
    # than at the end. A no-op for a file the page already wrote in order.
    ordered = {number: _problems[number] for number in sorted(_problems)}
    config.static_file_problems.write_text(dumps(ordered, indent=2))
    problems.clear_cache()
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
    return ExitCodes.EXIT_OK


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
    _problems: dict[int, dict[str, str | int | bool]] = {
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
    _problems[problem.number]['date'] = datetime.now().isoformat()
    _update_problems_state(_problems)
    return ExitCodes.EXIT_OK


if __name__ == '__main__':
    summary()

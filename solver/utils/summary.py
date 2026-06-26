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
from solver.shell.variables import variables
from solver.utils.path_utils import canonical_path


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


def _update_problems_state(_problems: dict[int, dict[str, str | int | bool]]) -> None:
    """Update the on-disk and in-memory problems state from parsed problem metadata.

    Args:
        _problems: Dictionary mapping problem numbers to their metadata
                  (title, level, pct, solved, date).
    """
    config.static_file_problems.write_text(dumps(_problems, indent=2))
    problems.clear_cache()


@register(help_text='Parse .progress.html into problems.json.', quietable=True)
def summary() -> int:
    """Refresh the solved/unsolved state from your Project Euler progress page.

    Parses `solutions/.progress.html` (the saved Page Source of your
    authenticated https://projecteuler.net/progress page) and updates
    `problems.json` with which problems are solved and their metadata. This is
    how the shell learns your real progress, driving `{solved}` / `{unsolved}`,
    `progress`, and `solved`.

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


@register(help_text='Print progress statistics about Euler problems.')
def progress() -> int:
    """Print overall progress through the Euler problems.

    Shows a bar of solved vs. unsolved problems, the solved count and
    percentage of the total known problems, and the next problem to solve (the
    lowest-numbered unsolved one). Reads the state maintained by `summary`; run
    `summary` first if your progress looks out of date.
    """
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


@register(
    help_text='Mark the workspace problem as solved, after checking.',
    aliases=('mark-solved',),
    quietable=True,
)
def mark() -> int:
    """Mark the workspace problem as solved — once its results confirm it.

    Records the current workspace problem as solved (with today's date) in
    `problems.json`, the same state `summary` maintains, so `{solved}`,
    `progress`, and `solved` reflect it without re-importing the progress page.

    It only proceeds after checking the recorded results: the workspace must
    hold a problem, its `test_cases.json` must have a `main` case with an
    answer, and `results.json` must contain a `correct` verdict for that `main`
    case. Run `benchmark` (which records results) first; a problem already
    marked solved is left unchanged.

    Aliased as `mark-solved`.
    """
    problem = variables.problem
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

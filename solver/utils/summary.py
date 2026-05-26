#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Progress: parse .progress.html into problems.json and refresh in-memory state."""
from __future__ import annotations

from datetime import datetime
from json import JSONDecodeError, dumps, loads
from typing import Any, Literal

from bs4 import BeautifulSoup, Tag

from solver.config import config
from solver.core.lock import check_workspace, check_workspace_lock
from solver.core.problems import Problem
from solver.shell import console, register
from solver.utils.path_utils import canonical_path
from solver.utils.visualize import reload_static_cache


def _parse_progress_html() -> dict[int, dict[str, str | int | bool]]:
    """Parse .progress.html and return problem metadata.

    Returns dict mapping problem_number -> {title, level, pct, solved, date}.
    level and pct are ints or '' when unknown; date is '' for unsolved problems.
    """
    progress_file = config.solutions_progress_file
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
    """Update the in-memory problems state from parsed problem metadata.

    Args:
        _problems: Dictionary mapping problem numbers to their metadata
                  (title, level, pct, solved, date).
    """
    config.solutions_problems_file.write_text(dumps(_problems, indent=2))
    problems_list: list[Problem] = [
        Problem(number=num, title=str(info['title']), difficulty=str(info['level']))
        for num, info in sorted(_problems.items(), key=lambda item: item[0])
    ]
    problems_dict: dict[int, Problem] = {problem.number: problem for problem in problems_list}
    solutions_history: dict[int, str] = {
        num: str(info['date'])
        for num, info in _problems.items() if info.get('date')
    }
    solved_problems: list[Problem] = [
        Problem(number=num, title=str(info['title']), difficulty=str(info['level']))
        for num, info in sorted(_problems.items(), key=lambda item: item[0])
        if info['solved'] and bool(info['date'])
    ]
    from solver.core.problems import problems
    problems.problems_list = problems_list
    problems.problems_dict = problems_dict
    problems.solutions_history = solutions_history
    problems.solved_problems = solved_problems
    reload_static_cache()


@register(name='summary',
          help='Parse .progress.html into problems.json and refresh in-memory state.',
          usage='summary', )
@check_workspace_lock
def solutions_summary() -> Literal['ok', 'nok']:
    _problems = _parse_progress_html()
    if not _problems:
        console.print(f'[error]error:[/error] [muted]{canonical_path(config.solutions_progress_file)} not found. '
                      'Summary generation aborted.[/muted]')
        return 'nok'
    _update_problems_state(_problems)
    return 'ok'


@register(name='mark-solved',
          help='Check and mark the problem currently in the workspace as solved.',
          usage='mark-solved', )
@check_workspace
def mark_solved() -> Literal['ok', 'nok']:
    problem = Problem.from_workspace()
    if problem is None:
        return 'nok'
    _problems: dict[int, dict[str, str | int | bool]] = {
        int(k): v
        for k, v in loads(config.solutions_problems_file.read_text()).items()
    }
    if _problems[problem.number]['solved']:
        console.print(f'[muted]Problem {problem.number} is already marked as solved.[/muted]')
        return 'ok'
    try:
        test_cases: list[dict[str, Any]] = loads((config.workspace_dir / config.test_cases_filename).read_text())
    except FileNotFoundError:
        console.print(f'[error]error:[/error] [muted]Test cases file not found for {problem}[/muted]')
        return 'nok'
    except JSONDecodeError:
        console.print(f'[error]error:[/error] [muted]Failed to parse test cases for {problem}[/muted]')
        return 'nok'
    main_test_case = next((tc for tc in test_cases if tc['category'] == 'main'), None)
    if main_test_case is None or main_test_case['answer'] is None:
        console.print(f'[error]error:[/error] [muted]{problem} is not solved.[/muted]')
        return 'nok'
    try:
        results: list[dict[str, Any]] = loads((config.workspace_dir / config.results_filename).read_text())
    except FileNotFoundError:
        console.print(f'[error]error:[/error] [muted]Results file not found for {problem}[/muted]')
        return 'nok'
    except JSONDecodeError:
        console.print(f'[error]error:[/error] [muted]Failed to parse results for {problem}[/muted]')
        return 'nok'
    correct: list[dict[str, Any]] = [r for r in results if r['verdict'] == 'correct' and r['category'] == 'main']
    if not correct:
        console.print(f'[error]error:[/error] [muted]{problem} is not solved.[/muted]')
        return 'nok'
    _problems[problem.number]['solved'] = True
    _problems[problem.number]['date'] = datetime.now().isoformat()
    _update_problems_state(_problems)
    return 'ok'


__all__ = ('solutions_summary', 'mark_solved',)

if __name__ == '__main__':
    solutions_summary()

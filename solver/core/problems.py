#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Project Euler scraper: fetches problem pages and builds standalone HTML with test cases and solution approach."""
from __future__ import annotations

from functools import lru_cache
from typing import NamedTuple

from bs4 import BeautifulSoup

from solver.core.config import config


class Problem(NamedTuple):
    number: int
    title: str
    difficulty: str

    def __str__(self) -> str:
        """Return a human-readable label in the form '<number>'."""
        return f'{self.number}:"{self.title}"'

    def as_title(self) -> str:
        """Return a human-readable label in the form '<number>: <title>'."""
        return f'Problem {self.number}: {self.title} [Level {self.difficulty}]'

    @classmethod
    def from_workspace(cls) -> Problem | None:
        """ Read the current workspace's problem number file and return the matching Problem. """
        try:
            problem_text = (config.workspace_dir / config.number_filename).read_text()
            number, title, difficulty = problem_text.split(':', maxsplit=2)
            return Problem(int(number), title, difficulty or '')
        except (FileNotFoundError, ValueError):
            return None

    @classmethod
    def from_number(cls, problem_number: int) -> Problem | None:
        """ Create a Problem instance from a given problem number. """
        try:
            return problems_dict[problem_number]
        except KeyError:
            return None

    def to_workspace(self) -> None:
        """Write the problem number to the workspace's problem number file."""
        (config.workspace_dir / config.number_filename).write_text(f'{self.number}:'
                                                                   f'{self.title}:'
                                                                   f'{self.difficulty or ""}')


# ---------------------------------------------------------------------------
# Parse solutions/progress.html
# ---------------------------------------------------------------------------

@lru_cache(maxsize=None)
def parse_progress_html() -> dict[int, dict[str, str | int | bool]]:
    """Parse .progress.html and return problem metadata.

    Returns dict mapping problem_number -> {title, level, pct, solved, date}.
    level and pct are ints or '' when unknown; date is '' for unsolved problems.
    """
    progress_file = config.solutions_progress_file
    if not progress_file.exists():
        return {}
    soup = BeautifulSoup(progress_file.read_text(encoding='utf-8', errors='replace'), 'html.parser')
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
        title = ''
        pct: int | str = ''
        date = ''
        tooltip = a_tag.find('span', class_='tooltiptext_narrow')
        if tooltip:
            for div in tooltip.find_all('div'):
                text = div.get_text(strip=True)
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
        solved = 'problem_solved' in (td.get('class') or [])
        _problems[num] = {'title': title, 'level': level, 'pct': pct, 'solved': solved, 'date': date}
    return _problems


problems_dict: dict[int, Problem] = {num: Problem(number=num, title=str(info['title']), difficulty=str(info['level']))
                                     for num, info in parse_progress_html().items()}
problems: list[Problem] = sorted(problems_dict.values(), key=lambda p: p.number)
solutions_history: dict[int, str] = {num: str(info['date'])
                                     for num, info in parse_progress_html().items() if info.get('date')}

__all__ = ('Problem', 'parse_progress_html', 'problems', 'problems_dict', 'solutions_history',)

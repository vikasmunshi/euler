#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Project Euler scraper: fetches problem pages and builds standalone HTML with test cases and solution approach."""
from __future__ import annotations

from functools import lru_cache
from json import loads
from typing import NamedTuple

from solver.config import config


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
            number, title, difficulty = problem_text.split('|', maxsplit=2)
            return Problem(int(number), title, difficulty or '')
        except (FileNotFoundError, ValueError):
            return None

    @classmethod
    def from_number(cls, problem_number: int) -> Problem | None:
        """ Create a Problem instance from a given problem number. """
        try:
            return problems.problems_dict[problem_number]
        except KeyError:
            return None

    def to_workspace(self) -> None:
        """Write the problem number to the workspace's problem number file."""
        (config.workspace_dir / config.number_filename).write_text(f'{self.number}|'
                                                                   f'{self.title}|'
                                                                   f'{self.difficulty or ""}')


@lru_cache(maxsize=None)
def get_problems() -> dict[int, dict[str, str | int | bool]]:
    """Retrieve problems from a cached problems.json."""
    return {int(k): v for k, v in loads(config.solutions_problems_file.read_text()).items()}


class problems:
    def __init__(self) -> None:
        raise TypeError('Config is a singleton class')

    problems_list: list[Problem] = [
        Problem(number=num, title=str(info['title']), difficulty=str(info['level']))
        for num, info in sorted(get_problems().items(), key=lambda item: item[0])
    ]
    problems_dict: dict[int, Problem] = {
        problem.number: problem
        for problem in problems_list
    }
    solutions_history: dict[int, str] = {
        num: str(info['date'])
        for num, info in get_problems().items() if info.get('date')
    }
    solved_problems: list[Problem] = [
        Problem(number=num, title=str(info['title']), difficulty=str(info['level']))
        for num, info in sorted(get_problems().items(), key=lambda item: item[0])
        if info['solved'] and bool(info['date'])
    ]


__all__ = ('Problem', 'problems')

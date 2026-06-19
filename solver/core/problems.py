#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The Problem model plus the projecteuler.net problem scraper and on-disk cache."""
from __future__ import annotations

__all__ = ['Problem', 'problems']

from functools import lru_cache
from json import loads
from typing import Callable, NamedTuple

from solver.config import config


def _parse_slice(slice_str: str) -> slice:
    """Parse a `[start:end:step]` string into a :class:`slice`.

    Brackets are optional and any non-integer field is treated as omitted, so
    a blank or malformed *slice_str* yields a full `slice(None, None, None)`.
    """
    if not slice_str:
        return slice(None, None, None)
    parts: list[int | None] = [None, None, None]
    for i, part in enumerate(slice_str.strip('[]').split(':')[:3]):
        try:
            parts[i] = int(part)
        except ValueError:
            pass
    start, end, step = parts
    return slice(start, end, step)


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
            problem_number: int = int((config.workspace_dir / config.number_filename).read_text())
            return problems.problems_dict[problem_number]
        except FileNotFoundError:
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
        (config.workspace_dir / config.number_filename).write_text(f'{self.number:04d}')


@lru_cache(maxsize=None)
def get_problems() -> dict[int, dict[str, str | int | bool]]:
    """Retrieve problems from a cached problems.json."""
    return {int(k): v for k, v in loads(config.static_file_problems.read_text()).items()}


@lru_cache(maxsize=None)
def get_notes_are_stale_func() -> Callable[[int], bool]:
    """Lazily import the notes_are_stale function. Stack already imports problems"""
    from solver.core.stack import notes_are_stale
    return notes_are_stale


class Problems:
    __slots__ = ('__problems_list', '__problems_dict', '__solutions_history',
                 '__solved_problems', '__not_solved_problems',)

    def __init__(self) -> None:
        self.__problems_list: list[Problem] = []
        self.__problems_dict: dict[int, Problem] = {}
        self.__solutions_history: dict[int, str] = {}
        self.__solved_problems: list[Problem] = []
        self.__not_solved_problems: list[Problem] = []

    def clear_cache(self) -> None:
        get_problems.cache_clear()
        self.__problems_list = []
        self.__problems_dict = {}
        self.__solutions_history = {}
        self.__solved_problems = []
        self.__not_solved_problems = []

    @property
    def last_problem(self) -> Problem:
        return self.problems_list[-1]

    @property
    def problems_list(self) -> list[Problem]:
        if not self.__problems_list:
            self.__problems_list = [
                Problem(number=num, title=str(info['title']), difficulty=str(info['level']))
                for num, info in sorted(get_problems().items(), key=lambda item: item[0])
            ]
        return self.__problems_list

    @property
    def problems_dict(self) -> dict[int, Problem]:
        if not self.__problems_dict:
            self.__problems_dict = {
                problem.number: problem
                for problem in self.problems_list
            }
        return self.__problems_dict

    @property
    def solutions_history(self) -> dict[int, str]:
        if not self.__solutions_history:
            self.__solutions_history = {
                num: str(info['date'])
                for num, info in get_problems().items() if info.get('date')
            }
        return self.__solutions_history

    @property
    def solved_problems(self) -> list[Problem]:
        if not self.__solved_problems:
            self.__solved_problems = [
                Problem(number=num, title=str(info['title']), difficulty=str(info['level']))
                for num, info in sorted(get_problems().items(), key=lambda item: item[0])
                if info['solved'] and bool(info['date'])
            ]
        return self.__solved_problems

    @property
    def not_solved_problems(self) -> list[Problem]:
        if not self.__not_solved_problems:
            solved_set: set[int] = {problem.number for problem in self.solved_problems}
            self.__not_solved_problems = [
                problem
                for problem in self.problems_list
                if problem.number not in solved_set
            ]
        return self.__not_solved_problems

    @property
    def stale_problems(self) -> list[Problem]:
        return [problem for problem in self.solved_problems if get_notes_are_stale_func()(problem.number)]

    @property
    def not_stale_problems(self) -> list[Problem]:
        stale_set: set[int] = {problem.number for problem in self.stale_problems}
        return [problem for problem in self.solved_problems if problem.number not in stale_set]

    def get_named_list(self, expr: str) -> list[Problem] | None:
        """Resolve a named-iterable expression to its problem list, else None.

        *expr* is a keyword — `problems`, `solved`/`!solved`, `stale`/`!stale` —
        optionally followed by a slice, e.g. `solved[0:5]`. The `!` forms map to
        the `not_*` properties. Returns None when the keyword is unknown, so
        callers can fall back to treating *expr* as a range/list literal.
        """
        name, bracket, _rest = expr.partition('[')
        attr = {
            'problems': 'problems_list',
            'solved': 'solved_problems',
            '!solved': 'not_solved_problems',
            'stale': 'stale_problems',
            '!stale': 'not_stale_problems',
        }.get(name)
        if attr is None:
            return None
        plist: list[Problem] = getattr(self, attr)
        return plist[_parse_slice(expr[len(name):])] if bracket else plist


problems = Problems()

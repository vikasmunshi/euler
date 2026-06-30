#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The Problem model plus the projecteuler.net problem scraper and on-disk cache."""
from __future__ import annotations

__all__ = ['Problem', 'problems']

from functools import lru_cache
from itertools import chain
from json import loads
from pathlib import Path
from random import choice
from typing import NamedTuple
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from bs4.element import AttributeValueList

from solver.config import config
from solver.core.download import download_file


@lru_cache(maxsize=None)
def solution_dir(problem_number: int) -> Path:
    """Return the solution directory for a problem."""
    if problem_number > 100:
        start_group: int = int(problem_number / 100) * 100
        end_group: int = start_group + 99
        return config.solutions_dir.joinpath('private', f'p{start_group:04d}_{end_group:04d}', f'p{problem_number:04d}')
    return config.solutions_dir.joinpath('public', f'p{problem_number:04d}')


@lru_cache(maxsize=None)
def get_problems() -> dict[int, dict[str, str | int | bool]]:
    """Retrieve problems from a cached problems.json."""
    return {int(k): v for k, v in loads(config.static_file_problems.read_text()).items()}


class Problem(NamedTuple):
    number: int
    title: str
    difficulty: str

    def __str__(self) -> str:
        """Return a compact label in the form '<number>:"<title>"'."""
        return f'{self.number}:"{self.title}"'

    def as_title(self) -> str:
        """Return a full label of the form 'Problem <number>: <title> [Level <difficulty>]'."""
        return f'Problem {self.number}: {self.title} [Level {self.difficulty}]'

    @property
    def solution_dir(self) -> Path:
        """The on-disk directory holding this problem's files (see module-level `solution_dir`)."""
        return solution_dir(self.number)

    def init(self, *, force_refresh: bool = False) -> None:
        """Download the problem statement and its resources into `solution_dir`.

        Fetches the projecteuler.net page for this problem, extracts the
        `problem_content` markup, downloads every referenced resource/image,
        rewrites the links to the local copies, and writes the statement plus an
        empty `__init__.py` into the solution directory.

        Args:
            force_refresh:  When True, bypass the download cache and re-fetch the
                            page and resources. Defaults to False.

        Raises:
            ValueError: if the page or any resource fails to download, or the
                        `problem_content` div is absent.
        """
        euler_url = urljoin(config.projecteuler_url, f'problem={self.number}')
        if (problem_html := download_file(euler_url, refresh=force_refresh)) is None:
            raise ValueError(f'Problem {self.number}: Failed to download HTML from {euler_url}')
        problem_soup: BeautifulSoup = BeautifulSoup(problem_html, 'html.parser')
        content: BeautifulSoup = problem_soup.find('div', {'class': 'problem_content'})  # type: ignore [assignment]
        if not content:
            raise ValueError(f'Problem {self.number}: Could not find problem_content div in HTML')
        files: dict[str, bytes] = {'__init__.py': b''}
        for element in chain(content.find_all('a'), content.find_all('img')):
            attr: str = {'a': 'href', 'img': 'src'}[element.name]
            src: str | AttributeValueList | None = element.get(attr)
            if src is None:
                continue
            if isinstance(src, str) and (src.startswith('resources/') or src.startswith('project/images/')):
                url: str = urljoin(config.projecteuler_url, src)
                local_filename: str = config.resource_dirname + '/' + src.split('/')[-1].split('?')[0]
                if (resource := download_file(url, refresh=force_refresh)) is None:
                    raise ValueError(f'Problem {self.number}: Failed to download {url}')
                files[local_filename] = resource
                element[attr] = local_filename
        files[config.statement_filename] = str(content).encode('utf-8')
        for filename, file_bytes in files.items():
            (self.solution_dir / filename).write_bytes(file_bytes)

    @property
    def problem_statement(self) -> str:
        """The saved HTML problem statement read from `solution_dir`."""
        return (self.solution_dir / config.statement_filename).read_text()

    @property
    def problem_resources(self) -> dict[str, bytes]:
        """Map each downloaded resource's relative path to its bytes (empty if none)."""
        if not (resources_path := self.solution_dir / config.resource_dirname).exists():
            return {}
        return {
            resource.relative_to(self.solution_dir).as_posix(): resource.read_bytes()
            for resource in resources_path.iterdir()
        }

    @classmethod
    def from_number(cls, problem_number: int) -> Problem:
        """ Create a Problem instance from a given problem number. """
        try:
            return problems.problems_dict[problem_number]
        except KeyError:
            raise ValueError(f'Problem {problem_number} not found') from None


class Problems:
    __slots__ = ('__problems_list', '__problems_dict', '__solutions_history', '__solved_problems',
                 '__unsolved_problems',)

    def __init__(self) -> None:
        self.__problems_list: list[Problem] = []
        self.__problems_dict: dict[int, Problem] = {}
        self.__solutions_history: dict[int, str] = {}
        self.__solved_problems: list[Problem] = []
        self.__unsolved_problems: list[Problem] = []

    def clear_cache(self) -> None:
        """Drop every memoised collection so they are rebuilt from `problems.json` on next access."""
        get_problems.cache_clear()
        self.__problems_list = []
        self.__problems_dict = {}
        self.__solutions_history = {}
        self.__solved_problems = []
        self.__unsolved_problems = []

    @property
    def last_problem(self) -> Problem:
        """The highest-numbered known problem."""
        return self.problems_list[-1]

    @property
    def next_unsolved_problem(self) -> Problem:
        """The lowest-numbered problem without a recorded solution."""
        return self.unsolved_problems[0]

    @property
    def random_problem(self) -> Problem:
        """A randomly chosen unsolved problem (or any problem if all are solved)."""
        return choice(problems.unsolved_problems or problems.problems_list)

    @property
    def problems_list(self) -> list[Problem]:
        """All known problems, ascending by number (built lazily and cached).

        On first build, any problem whose `solution_dir` is missing is `init()`-ed
        (its statement and resources downloaded), so accessing this can have the
        side effect of populating the stack.
        """
        if not self.__problems_list:
            self.__problems_list = [
                Problem(number=num, title=str(info['title']), difficulty=str(info['level']))
                for num, info in sorted(get_problems().items(), key=lambda item: item[0])
            ]
            for problem in self.__problems_list:
                if not problem.solution_dir.exists():
                    problem.init()
        return self.__problems_list

    @property
    def problems_dict(self) -> dict[int, Problem]:
        """All known problems keyed by number (built lazily and cached)."""
        if not self.__problems_dict:
            self.__problems_dict = {
                problem.number: problem
                for problem in self.problems_list
            }
        return self.__problems_dict

    @property
    def solutions_history(self) -> dict[int, str]:
        """Map each solved problem's number to its recorded solve date (built lazily and cached)."""
        if not self.__solutions_history:
            self.__solutions_history = {
                num: str(info['date'])
                for num, info in get_problems().items() if info.get('date')
            }
        return self.__solutions_history

    @property
    def solved_problems(self) -> list[Problem]:
        """Problems flagged solved with a recorded date, ascending by number (built lazily and cached)."""
        if not self.__solved_problems:
            self.__solved_problems = [
                Problem(number=num, title=str(info['title']), difficulty=str(info['level']))
                for num, info in sorted(get_problems().items(), key=lambda item: item[0])
                if info['solved'] and bool(info['date'])
            ]
        return self.__solved_problems

    @property
    def unsolved_problems(self) -> list[Problem]:
        """Known problems not in `solved_problems`, ascending by number (built lazily and cached)."""
        if not self.__unsolved_problems:
            solved_set: set[int] = {problem.number for problem in self.solved_problems}
            self.__unsolved_problems = [
                problem
                for problem in self.problems_list
                if problem.number not in solved_set
            ]
        return self.__unsolved_problems


problems: Problems = Problems()

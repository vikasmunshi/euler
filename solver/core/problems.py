#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The Problem model plus the projecteuler.net problem scraper and on-disk cache."""
from __future__ import annotations

__all__ = ['Problem', 'SOLVED_DATE_FORMAT', 'format_solved_date', 'parse_solved_date', 'problems', 'solution_dir']

from datetime import datetime
from functools import lru_cache
from itertools import chain
from json import JSONDecodeError, loads
from pathlib import Path
from random import choice
from subprocess import run
from typing import Literal, NamedTuple, NotRequired, TypedDict
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from bs4.element import AttributeValueList
from requests import RequestException

from solver.config import config
from solver.core.download import download_file


SOLVED_DATE_FORMAT: str = '%a, %d %b %Y, %H:%M'
"""How a solved date is written in `problems.json` — the progress page's own wording.

The field has two writers: the projecteuler.net progress page (scraped verbatim by
`solver.core.progress`, via `summary` and the web upload) and the `mark` command. Both
must speak this one format, or the record the second one writes is unreadable to
everything that reads the first.
"""


def format_solved_date(when: datetime) -> str:
    """Render *when* the way `problems.json` records a solved date."""
    return when.strftime(SOLVED_DATE_FORMAT)


def parse_solved_date(text: str) -> datetime | None:
    """Read a `problems.json` solved date, or `None` when there is nothing readable there.

    ISO-8601 is accepted as well as :data:`SOLVED_DATE_FORMAT`: `mark` wrote its dates that
    way until this was fixed, so a clone or a backup can still carry them. An unparseable
    date is a missing date, not an error — one malformed record must not take down every
    caller that only wanted the latest one.
    """
    if not text:
        return None
    try:
        return datetime.strptime(text, SOLVED_DATE_FORMAT)
    except ValueError:
        pass
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


@lru_cache(maxsize=None)
def solution_dir(problem_number: int) -> Path:
    """Return the solution directory for a problem."""
    if problem_number > 100:
        start_group: int = problem_number // 100 * 100
        end_group: int = start_group + 99
        return config.solutions_dir.joinpath('private', f'p{start_group:04d}_{end_group:04d}', f'p{problem_number:04d}')
    return config.solutions_dir.joinpath('public', f'p{problem_number:04d}')


class ProblemInfoDict(TypedDict):
    title: str
    level: int | Literal['']
    pct: int | Literal['']
    solvers: NotRequired[int | Literal['']]
    solved: bool
    date: str


@lru_cache(maxsize=None)
def get_problems() -> dict[int, ProblemInfoDict]:
    """Retrieve problems from a cached problems.json.

    A worktree copy that does not parse — in practice, git conflict markers left by a sync
    that stopped part-way — falls back to the committed copy at HEAD, with a warning. Every
    shell start reads this file before the first prompt, so letting it raise crashed the
    shell and locked its owner out of `git-reset --hard`, the one verb that repairs it.
    """
    try:
        return {int(k): v for k, v in loads(config.static_file_problems.read_text()).items()}
    except JSONDecodeError as exc:
        rel = config.static_file_problems.relative_to(config.root_dir).as_posix()
        committed = run(['git', 'show', f'HEAD:{rel}'], cwd=config.root_dir, capture_output=True, text=True)
        if committed.returncode != 0:
            raise
        from solver.shell import console  # lazily: solver.shell imports this module
        console.print(f'[warning]{rel} does not parse ({exc.msg}, line {exc.lineno}) — likely an '
                      'unresolved merge conflict; using the committed copy. Run '
                      '[accent]git-reset --hard[/accent] to repair this clone.[/warning]')
        return {int(k): v for k, v in loads(committed.stdout).items()}


class Problem(NamedTuple):
    number: int
    title: str
    difficulty: str

    def __str__(self) -> str:
        """Return a compact label in the form '<number>:"<title>"'."""
        return f'{self.number}:"{self.title}"'

    def as_title(self) -> str:
        """Return a full label of the form 'Problem <number>: <title> [Level <difficulty>]'.

        The level is left off for a problem projecteuler.net has not rated yet (`difficulty`
        is `''` until it has), rather than rendering an empty `[Level ]`.
        """
        level: str = f' [Level {self.difficulty}]' if self.difficulty else ''
        return f'Problem {self.number}: {self.title}{level}'

    @property
    def solution_dir(self) -> Path:
        """The on-disk directory holding this problem's files (see module-level `solution_dir`)."""
        return solution_dir(self.number)

    def init(self, *, force_refresh: bool = False) -> list[Path]:
        """Download the problem statement and its resources into `solution_dir`.

        Fetches the projecteuler.net page for this problem, extracts the
        `problem_content` markup, downloads every referenced resource/image,
        rewrites the links to the local copies, and writes the statement plus an
        empty `__init__.py` into the solution directory.

        Args:
            force_refresh:  When True, bypass the download cache and re-fetch the
                            page and resources. Defaults to False.

        Nothing is written unless everything downloaded: the files are collected first and
        written together at the end, so a failure leaves no half-populated directory.

        Returns:
            Every file written, so a caller can stage exactly those (`summary` commits them).

        Raises:
            ValueError: if the page or any resource fails to download, the
                        `problem_content` div is absent, or two resources would be
                        saved under the same local name.
        """
        euler_url = urljoin(config.projecteuler_url, f'problem={self.number}')
        problem_html: bytes = self._download(euler_url, refresh=force_refresh)
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
                resource: bytes = self._download(url, refresh=force_refresh)
                # Saved by basename alone, so two remote folders can offer the same name; the
                # second would silently overwrite the first, and both links show one file.
                if files.get(local_filename, resource) != resource:
                    raise ValueError(f'Problem {self.number}: two resources would both be saved '
                                     f'as {local_filename}')
                files[local_filename] = resource
                element[attr] = local_filename
        files[config.statement_filename] = str(content).encode('utf-8')
        written: list[Path] = []
        for filename, file_bytes in files.items():
            file: Path = self.solution_dir / filename
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(file_bytes)
            written.append(file)
        return written

    def _download(self, url: str, *, refresh: bool) -> bytes:
        """`download_file`, with any network or HTTP failure raised as the `ValueError` `init` promises."""
        try:
            return download_file(url, refresh=refresh)
        except RequestException as exc:
            raise ValueError(f'Problem {self.number}: failed to download {url}: {exc}') from exc

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
            for resource in resources_path.iterdir() if resource.is_file()
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
        """Drop every memoized collection so they are rebuilt from `problems.json` on next access."""
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
    def last_solved_problem(self) -> Problem:
        """The latest solved `problem`."""
        result: Problem = self.problems_list[0]
        latest_solved: datetime | None = None
        for num, info in get_problems().items():
            if not info['solved']:
                continue
            solved = parse_solved_date(info['date'])
            if solved is None:
                continue
            if not latest_solved or solved > latest_solved:
                result = Problem.from_number(num)
                latest_solved = solved
        return result

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

        A pure read of `problems.json`: no problem is downloaded here. It used to `init()`
        every problem whose directory was missing, which made any lookup a network call
        and, on a clone's first run, wrote statement files that then collided with the same
        files arriving by `git-sync`. New problems are fetched where they are discovered —
        `summary`, which writes `problems.json` (see `missing_problems`).
        """
        if not self.__problems_list:
            self.__problems_list = [
                Problem(number=num, title=info['title'], difficulty=str(info['level']))
                for num, info in sorted(get_problems().items(), key=lambda item: item[0])
            ]
        return self.__problems_list

    @property
    def missing_problems(self) -> list[Problem]:
        """Known problems with no `solution_dir` yet — the ones `init()` has not fetched."""
        return [problem for problem in self.problems_list if not problem.solution_dir.exists()]

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
                Problem.from_number(num)
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

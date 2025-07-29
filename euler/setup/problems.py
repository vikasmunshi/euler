#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Solution implementations for Project Euler problems."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from fcntl import LOCK_EX, LOCK_UN, flock
from functools import lru_cache
from importlib import import_module
from os import utime
from pathlib import Path
from textwrap import fill
from typing import Any, ClassVar, Generator, Literal, cast

from bs4 import BeautifulSoup
from bs4.element import Tag
from yaml import Dumper, ScalarNode, YAMLError, dump as dump_yaml, safe_load as load_yaml

from euler.logger import logger
from euler.setup.base_dir import base_dir
from euler.setup.cached_requests import get_text_file

__all__ = ['ProblemInfo', 'TestCase', 'canonical_name']


@dataclass(frozen=True, slots=True, kw_only=True, eq=True)
class TestCase:
    answer: Any | None = field(compare=True)
    is_main_case: bool = field(compare=True)
    kwargs: dict[str, Any] = field(compare=True)
    solution_execution_time: float | None = field(default=None, compare=False)
    solved: bool = field(default=False, compare=False)

    def as_dict(self) -> dict:
        return asdict(self)

    def f_str(self) -> str:
        return (f'TestCase(\n'
                f'answer={self.answer!r},\n'
                f'is_main_case={self.is_main_case!r},\n'
                f'kwargs={self.kwargs!r},\n'
                f'solution_execution_time={self.solution_execution_time!r},\n'
                f'solved={self.solved!r}\n'
                f')')

    @classmethod
    def from_dict(cls, data: dict) -> TestCase:
        answer: int | None = data.pop('answer', None)
        is_main_case: bool = data.pop('is_main_case', False)
        solution_execution_time: float | None = data.pop('solution_execution_time', None)
        solved: bool = data.pop('solved', False)
        kwargs: dict[str, Any] = data.pop('kwargs', data)
        return cls(answer=answer, is_main_case=is_main_case, kwargs=kwargs,
                   solution_execution_time=solution_execution_time, solved=solved, )


@dataclass(frozen=True, slots=True, kw_only=True)
class ProblemInfo:
    name: str
    number: int
    problem_statement: str
    solution_approach: str = field(default='Document the mathematical approach here.\n')
    solved: bool = field(default=False)
    test_cases: list[TestCase] = field(default_factory=list)
    url: str
    valid_fields: ClassVar[set[str]] = {'name', 'number', 'problem_statement', 'solution_approach', 'test_cases', 'url'}

    def __post_init__(self) -> None:
        if not self.test_cases:
            self.test_cases.append(TestCase(answer=0, is_main_case=False, kwargs={'n': 0}))
        if len(list(filter(lambda x: x.is_main_case, self.test_cases))) > 1:
            raise ValueError(f'Problem {self.number} has more than one main test case')

    def as_dict(self) -> dict:
        return asdict(self)

    def to_yaml(self) -> None:
        with open(self.yaml_file, 'w') as f:
            flock(f.fileno(), LOCK_EX)
            dump_yaml(self.as_dict(), f, indent=2, Dumper=ProblemInfoDumper)
            flock(f.fileno(), LOCK_UN)
        logger.info({'action': 'problem_info_saved', 'number': self.number, 'file': self.yaml_file.name})

    @classmethod
    def from_dict(cls, data: dict) -> ProblemInfo:
        data['test_cases'] = [TestCase.from_dict(test_case) for test_case in data.get('test_cases', [])]
        return cls(**{k: v for k, v in data.items() if k in cls.valid_fields})

    @classmethod
    def from_yaml(cls, problem_number: int) -> ProblemInfo:
        yaml_file: Path = base_dir / (canonical_name(problem_number) + '.yaml')
        with open(yaml_file, 'r') as f:
            flock(f.fileno(), LOCK_EX)
            data = load_yaml(f)
            flock(f.fileno(), LOCK_UN)
        return cls.from_dict(data)

    @property
    def module_name(self) -> str:
        return f'euler.{canonical_name(self.number, connector=".")}'

    @property
    def python_file(self) -> Path:
        return base_dir / (canonical_name(self.number) + '.py')

    @property
    def yaml_file(self) -> Path:
        return base_dir / (canonical_name(self.number) + '.yaml')

    @classmethod
    def load(cls, first: int = 1, last: int = 950,
             refresh: Literal['always', 'missing', 'never'] = 'never', ) -> Generator[ProblemInfo, None, None]:
        if refresh == 'never':
            yield from (cls.from_yaml(problem_number=problem_number) for problem_number in range(first, last + 1))
        elif refresh == 'missing':
            for problem_number in range(first, last + 1):
                try:
                    yield cls.from_yaml(problem_number=problem_number)
                except (FileNotFoundError, YAMLError):
                    yield cls.refresh(problem_number=problem_number)
        elif refresh == 'always':
            yield from (cls.refresh(problem_number=problem_number) for problem_number in range(first, last + 1))
        else:
            raise ValueError(f'Invalid refresh option: {refresh}')

    @classmethod
    def refresh(cls, problem_number: int) -> ProblemInfo:
        url: str = f'https://projecteuler.net/problem={problem_number}'
        content: Tag = cast(Tag, BeautifulSoup(get_text_file(url), 'html.parser').find('div', id='content'))
        title_tag: Tag = cast(Tag, content.find('h2'))
        title: str = clean_up_name(title_tag.get_text().strip('\n'), problem_number=problem_number).lower()
        statement_tag: Tag = cast(Tag, content.find('div', class_='problem_content'))
        statement: str = clean_up_statement(statement_tag.get_text().strip('\n'))
        info: ProblemInfo = cls(number=problem_number, url=url, name=title, problem_statement=statement)
        info.sync_test_cases_from_python_to_data_object()
        info.to_yaml()
        return info

    def sync(self, direction: Literal['auto', 'yaml to py', 'py to yaml'] = 'auto') -> None:
        yaml_file, py_file = self.yaml_file, self.python_file
        yaml_file_stat, py_file_stat = yaml_file.stat(), py_file.stat()
        yaml_m_time, yaml_atime = yaml_file_stat.st_mtime, yaml_file_stat.st_atime
        py_m_time, py_atime = py_file_stat.st_mtime, py_file_stat.st_atime

        def yaml_to_py() -> None:
            self.sync_doc_and_test_cases_from_data_object_to_python_file()
            utime(py_file, (py_atime, yaml_m_time))
            logger.info({'action': 'problem_info_synced', 'number': self.number, 'direction': 'yaml to py'})

        def py_to_yaml() -> None:
            self.sync_test_cases_from_python_to_data_object()
            self.to_yaml()
            utime(yaml_file, (yaml_atime, py_m_time))
            logger.info({'action': 'problem_info_synced', 'number': self.number, 'direction': 'py to yaml'})

        func = yaml_to_py if direction == 'yaml to py' else py_to_yaml if direction == 'py to yaml' else None
        if not func:
            func = yaml_to_py if yaml_m_time > py_m_time else py_to_yaml if py_m_time > yaml_m_time else None
        if func:
            func()
        else:
            logger.info({'action': 'problem_info_no_sync', 'number': self.number})

    def sync_test_cases_from_python_to_data_object(self) -> None:
        if self.python_file.exists():
            try:
                module = import_module(self.module_name)
            except ImportError as e:
                logger.error({'action': 'problem_info_import_error', 'number': self.number, 'error': str(e)})
            else:
                if hasattr(module, 'test_cases'):
                    if test_cases := getattr(module, 'test_cases'):
                        self.test_cases.clear()
                        self.test_cases.extend(test_cases)

    def sync_doc_and_test_cases_from_data_object_to_python_file(self) -> None:
        source_lines: list[str] = self.python_source_code().splitlines(keepends=True)
        replace_line: bool = False
        is_docstring: bool = True
        for i, line in enumerate(source_lines):
            if is_docstring and (line.startswith('from') or line.startswith('import')):
                is_docstring = False
            if is_docstring:
                source_lines[i] = ''
            elif line.lower().startswith(r'test_cases: list['):
                source_lines[i] = self.python_test_cases_from_yaml()
                replace_line = True
            elif replace_line and ((is_closing := line.startswith(']')) or
                                   line.startswith('@register_solution') or
                                   line.startswith('def ') or
                                   line.startswith('# Register ')):
                if is_closing:
                    source_lines[i] = ''
                replace_line = False
            elif replace_line:
                source_lines[i] = ''
        with open(self.python_file, 'w') as f:
            flock(f.fileno(), LOCK_EX)
            f.write(self.python_file_header_from_yaml() + '\n' + ''.join(source_lines))
            flock(f.fileno(), LOCK_UN)
        logger.info({'action': 'problem_info_synced', 'number': self.number, 'file': self.python_file.name})

    def python_source_code(self) -> str:
        if self.python_file.exists():
            return self.python_file.read_text()
        indent = ' ' * 4
        return (f'{self.python_file_header_from_yaml()}\n'
                'from __future__ import annotations\n\n'
                'from euler.evaluator import evaluate_solutions, register_solution\n'
                'from euler.setup import TestCase\n\n'
                f'{self.python_test_cases_from_yaml()}\n\n'
                f'# Register this function as a solution for problem #{self.number}\n'
                f'@register_solution(problem_number={self.number}, test_cases=test_cases)\n'
                f'def {self.function_signature()}:\n'
                f"{indent}print('Implement solution body for Euler Problem {self.number}: {self.name}')\n"
                f'{indent}raise NotImplementedError\n\n\n'
                "if __name__ == '__main__':\n"
                f'{indent}# Run solution tests and exit with success (0) or failure (>0) status code\n'
                f'{indent}raise SystemExit(evaluate_solutions({self.number}))')

    def function_signature(self) -> str:
        main_test_case = next(filter(lambda x: x.is_main_case, self.test_cases), None) or self.test_cases[0]
        return_type: str = 'int' if main_test_case.answer is None else type(main_test_case.answer).__name__
        if main_test_case.kwargs:
            kwargs = ', '.join(f'{k}: {type(v).__name__}' for k, v in main_test_case.kwargs.items())
            return f'{self.name}(*, {kwargs}) -> {return_type}'
        else:
            return f'{self.name}() -> {return_type}'

    def python_test_cases_from_yaml(self) -> str:
        return f"test_cases: list[TestCase] = [\n    {',\n    '.join(case.f_str() for case in self.test_cases)},\n]\n"

    def python_file_header_from_yaml(self) -> str:
        answer = next(filter(lambda x: x.is_main_case, self.test_cases), None)
        indent = ' ' * 2
        return ('#!/usr/bin/env python3\n'
                '# -*- coding: utf-8 -*-\n'
                f'r""" Solution to Project Euler problem {self.number}: {self.name}\n\n'
                'Problem Statement:\n'
                f'{indent}{indent.join(self.problem_statement.splitlines(keepends=True))}\n'
                'Solution Approach:\n'
                f'{indent}{indent.join(self.solution_approach.splitlines(keepends=True))}\n'
                f'URL: {self.url}\n'
                f'Answer: {answer.answer if answer else None}\n'
                '"""')


class ProblemInfoDumper(Dumper):
    def represent_scalar(self, tag: str, value: Any, style: str | None = None) -> ScalarNode:
        if isinstance(value, str) and '\n' in value:  # Use block literal `|` for multiline strings
            style = '|'
        return super().represent_scalar(tag, value, style)


@lru_cache(maxsize=None)
def canonical_name(problem_number: int, *, connector: Literal['.', '/'] = '/') -> str:
    return f'solutions{connector}set_{problem_number // 100:04d}{connector}solution_{problem_number:06d}'


def clean_up_name(name: str, problem_number: int) -> str:
    if name.isidentifier():
        return name
    for k, v in _name_replacements.items():
        name = name.replace(k, v)
    if name[0].isdigit():
        name = 'solution_' + name
    if not name.isidentifier():
        name = f'solution_{problem_number}'
    return name


def clean_up_statement(statement: str) -> str:
    for k, v in _content_replacements.items():
        statement = statement.replace(k, v)
    statement = fill(statement, width=80, tabsize=2)
    return statement + '\n'


_name_replacements: dict[str, str] = {
    "'": '_',
    ' ': '_',
    '!': '',
    '"': '',
    '#': '',
    '$': '',
    '%': '',
    '&': '',
    '(': '',
    ')': '',
    '*': '_',
    '+': '_',
    ',': '',
    '-': '_',
    '.': '',
    '/': '',
    ':': '',
    ';': '',
    '<': '',
    '=': '',
    '>': '',
    '?': '',
    '@': '',
    '[': '',
    '\\': '',
    ']': '',
    '^': '',
    '`': '',
    '{': '',
    '|': '',
    '}': '',
    '~': '',
}

_content_replacements: dict[str, str] = {
    r'$': '',
    r'\dots': '...',
    r'\times': '*',
}

if __name__ == '__main__':
    logger.setLevel('INFO')
    count: int = 0
    for count, problem in enumerate(ProblemInfo.load(first=1, last=950, refresh='missing'), start=1):
        problem.sync(direction='auto')
        # problem.sync(direction='py to yaml')
        # problem.sync(direction='yaml to py')
    print(f'Synced {count} problems')

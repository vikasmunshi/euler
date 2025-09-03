#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Solution registry for Project Euler problems."""
from __future__ import annotations

from dataclasses import dataclass
from json import dump, load
from pathlib import Path
from sys import modules
from typing import Any, Callable, ClassVar, Literal, ParamSpec, Protocol, TypeVar, cast

from euler_solver.setup.file_lock import FileLock
from euler_solver.setup.paths import MAX_SHARABLE, get_answers_path

PS = ParamSpec('PS')
RT = TypeVar('RT', covariant=True, )
FS = Callable[PS, RT]


class Solution(Protocol[PS, RT]):
    def __call__(self, *args: PS.args, **kwargs: PS.kwargs) -> RT: ...

    __name__: str
    __doc__: str | None
    __module__: str
    __qualname__: str
    __defaults__: tuple[Any, ...] | None
    __code__: Any
    __globals__: dict[str, Any]
    __dict__: dict[str, Any]
    __closure__: tuple[Any, ...] | None
    __annotations__: dict[str, Any]
    __kwdefaults__: dict[str, Any] | None
    euler_problem: int
    test_cases: tuple[TestCase, ...]


ST = Solution[PS, RT]


@dataclass(frozen=True, kw_only=True, slots=True)
class TestCase:
    answer: Any | None
    category: Literal['preliminary', 'main', 'extended']
    input: dict[str, Any]
    key: str

    def execution_time_key(self, solution: Solution) -> str:
        return f'{solution.__name__}_{self.key}'


@dataclass(frozen=True, kw_only=True, slots=True)
class SolutionRegistry:
    """Registry for Project Euler solutions."""
    # Class attributes.
    framework_version: ClassVar[str] = '0.2.1'
    evaluate_preliminary_test_cases: ClassVar[bool] = True
    evaluate_main_test_cases: ClassVar[bool] = True
    evaluate_extended_test_cases: ClassVar[bool] = True
    ignore_test_case_slices: ClassVar[bool] = False
    instances: ClassVar[dict[int, SolutionRegistry]] = {}
    # Instance attributes
    euler_problem: int
    is_private: bool
    solutions: list[Solution]
    test_case_answers: dict[str, Any]
    test_case_answers_file: Path
    test_cases: tuple[TestCase, ...]
    url: str

    @classmethod
    def set_evaluation_options(cls, *,
                               eval_preliminary: bool = False,
                               eval_main: bool = True,
                               eval_extended: bool = False,
                               ignore_slices: bool = False,
                               ) -> None:
        cls.evaluate_preliminary_test_cases = eval_preliminary
        cls.evaluate_main_test_cases = eval_main
        cls.evaluate_extended_test_cases = eval_extended
        cls.ignore_test_case_slices = ignore_slices

    @classmethod
    def put(cls, euler_problem: int, solution: Solution) -> SolutionRegistry:
        if euler_problem in cls.instances:
            instance: SolutionRegistry = cls.instances[euler_problem]
            instance.solutions.append(solution)
            return instance
        answers: dict[str, Any] = {}
        if not (answers_file := get_answers_path(euler_problem)).exists():
            with FileLock(answers_file, 'write') as f:
                dump(answers, f)
        else:
            with FileLock(answers_file, 'read') as f:
                answers = load(f)
        test_cases: tuple[TestCase, ...] = tuple(
                [
                    TestCase(**test_case,
                             key=(key := cls.format_kwargs(test_case['input'])),
                             answer=answers.get(key))
                    for test_case in getattr(modules[solution.__module__], 'test_cases', [])
                ]
        )
        instance = cls(
                euler_problem=euler_problem,
                is_private=euler_problem > MAX_SHARABLE,
                solutions=[solution],
                test_case_answers=answers,
                test_case_answers_file=answers_file,
                test_cases=test_cases,
                url=f'https://projecteuler.net/problem={euler_problem}',
        )
        cls.instances[euler_problem] = instance
        return instance

    @classmethod
    def get(cls, euler_problem: int) -> SolutionRegistry | None:
        return cls.instances.get(euler_problem, None)

    @classmethod
    def register_solution(cls,
                          euler_problem: int,
                          max_test_case: int | None = None,
                          allow_max_override: bool = True) -> Callable[[FS], ST]:
        def wrapper(func: FS) -> ST:
            solution = cast(ST, func)
            if getattr(func, '__module__', '') == '__main__':
                return solution
            instance: SolutionRegistry = cls.put(euler_problem, solution)
            if (max_test_case is None) or (allow_max_override and cls.ignore_test_case_slices):
                max_tc_index: int = len(instance.test_cases)
            else:
                max_tc_index = max_test_case
            solution.euler_problem = euler_problem
            solution.test_cases = tuple(test_case for test_case in instance.test_cases[:max_tc_index + 1]
                                        if (cls.evaluate_preliminary_test_cases and test_case.category == 'preliminary')
                                        or (cls.evaluate_main_test_cases and test_case.category == 'main')
                                        or (cls.evaluate_extended_test_cases and test_case.category == 'extended'))
            return solution

        return wrapper

    @staticmethod
    def format_kwargs(kwargs: dict[str, Any]) -> str:
        return ', '.join(sorted(f'{key}={val}' for key, val in kwargs.items()))


get_registry = SolutionRegistry.get
register_solution = SolutionRegistry.register_solution
set_evaluation_options = SolutionRegistry.set_evaluation_options

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Solution registry for Project Euler problems."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import StrEnum
from functools import lru_cache
from json import JSONDecodeError, load
from sys import modules
from typing import Any, Callable, ClassVar, Literal, ParamSpec, Protocol, TypeVar, cast

from euler_solver.framework.file_lock import FileLock
from euler_solver.framework.paths import MAX_SHARABLE, get_evaluation_log_path

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


class Status(StrEnum):
    correct = 'correct'
    recorded = 'recorded'
    incorrect = 'incorrect'
    undecided = 'undecided'
    unsolved = 'unsolved'


@dataclass(frozen=True, kw_only=True, slots=True)
class TestCase:
    answer: Any | None = field(default=None)
    category: Literal['dev', 'main', 'extra']
    input: dict[str, Any]

    def __hash__(self) -> int:
        return hash(repr(self.input))

    def check_answer(self, answer: Any, record: bool = False) -> Status:
        result: Status
        if answer is NotImplemented or answer is None:
            result = Status.unsolved
        elif record:
            if self.answer is None:
                object.__setattr__(self, 'answer', answer)
            result = Status.recorded
        elif self.answer is None:
            result = Status.undecided
        elif answer == self.answer:
            result = Status.correct
        else:
            result = Status.incorrect
        return result


@dataclass(frozen=True, kw_only=True, slots=True)
class SolutionRegistry:
    """Registry for Project Euler solutions."""
    # Class attributes.
    framework_version: ClassVar[str] = '0.2.1'
    evaluate_dev_test_cases: ClassVar[bool] = True
    evaluate_main_test_cases: ClassVar[bool] = True
    evaluate_extra_test_cases: ClassVar[bool] = True
    ignore_test_case_slices: ClassVar[bool] = False
    instances: ClassVar[dict[int, SolutionRegistry]] = {}
    # Instance attributes
    euler_problem: int
    evaluation_log: dict[str, float]
    is_private: bool
    solutions: list[Solution]
    test_cases: list[TestCase]
    unsolved_test_cases: bool
    url: str

    @classmethod
    def set_evaluation_options(cls, *,
                               eval_dev: bool = False,
                               eval_main: bool = True,
                               eval_extra: bool = False,
                               ignore_slices: bool = False,
                               ) -> None:
        cls.evaluate_dev_test_cases = eval_dev
        cls.evaluate_main_test_cases = eval_main
        cls.evaluate_extra_test_cases = eval_extra
        cls.ignore_test_case_slices = ignore_slices

    @classmethod
    def put(cls, euler_problem: int, solution: Solution) -> SolutionRegistry:
        if euler_problem in cls.instances:
            instance: SolutionRegistry = cls.instances[euler_problem]
            instance.solutions.append(solution)
            return instance
        evaluation_log: dict[str, float] = {}
        test_cases: list[TestCase] = [TestCase(**tc) for tc in getattr(modules[solution.__module__], 'test_cases', [])]
        unsolved_test_cases: bool = any(tc.answer is None for tc in test_cases)
        if not unsolved_test_cases:
            try:
                with FileLock(get_evaluation_log_path(euler_problem), 'read') as f:
                    evaluation_log = {k: float(v) for k, v in load(f).items()}
            except (FileNotFoundError, JSONDecodeError,):
                evaluation_log = {}
        instance = cls(
                euler_problem=euler_problem,
                evaluation_log=evaluation_log,
                is_private=euler_problem > MAX_SHARABLE,
                solutions=[solution],
                test_cases=test_cases,
                unsolved_test_cases=unsolved_test_cases,
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
                          max_test_case_index: int | None = None,
                          allow_max_override: bool = True) -> Callable[[FS], ST]:
        def wrapper(func: FS) -> ST:
            solution = cast(ST, func)
            if getattr(func, '__module__', '') == '__main__':
                return solution
            instance: SolutionRegistry = cls.put(euler_problem, solution)
            if (max_test_case_index is None) or (allow_max_override and cls.ignore_test_case_slices):
                max_tc_index: int = len(instance.test_cases)
            else:
                max_tc_index = max_test_case_index
            solution.euler_problem = euler_problem
            solution.test_cases = tuple(test_case for test_case in instance.test_cases[:max_tc_index + 1]
                                        if (cls.evaluate_dev_test_cases and test_case.category == 'dev')
                                        or (cls.evaluate_main_test_cases and test_case.category == 'main')
                                        or (cls.evaluate_extra_test_cases and test_case.category == 'extra'))
            if not solution.test_cases:
                solution.test_cases = tuple(tc for tc in instance.test_cases if tc.category == 'main')
            if not solution.test_cases:
                raise NotImplementedError(f'No test cases for problem {euler_problem}.')
            for test_case in instance.test_cases:
                func_def = get_func_def(test_case, solution.__name__)
                if func_def not in instance.evaluation_log:
                    instance.evaluation_log[func_def] = float('nan')
            return solution

        return wrapper

    def get_execution_time(self, func_def: str) -> float:
        execution_time: float = self.evaluation_log.get(func_def, float('nan'))
        return execution_time

    def set_execution_time(self, func_def: str, execution_time: float) -> None:
        current_execution_time: float = self.evaluation_log.get(func_def, float('nan'))
        if math.isnan(current_execution_time):
            self.evaluation_log[func_def] = execution_time
        elif current_execution_time > execution_time:
            self.evaluation_log[func_def] = execution_time


@lru_cache(maxsize=None)
def get_func_def(test_case: TestCase, solution_name: str) -> str:
    return f'{solution_name}({format_kwargs(test_case.input)})'


def format_kwargs(kwargs: dict[str, Any]) -> str:
    return ', '.join(sorted(f'{key}={format_val(key, val)}' for key, val in kwargs.items()))


def format_val[T](key: str, val: T) -> T | str:
    if isinstance(val, int) and val > 1_000_000_000 and val % 10 == 0:
        return f'{val:6e}'
    if key == 'file_url' and isinstance(val, str) and val.startswith('https://'):
        return val.split('/')[-1]
    return val


get_registry = SolutionRegistry.get
register_solution = SolutionRegistry.register_solution
set_evaluation_options = SolutionRegistry.set_evaluation_options

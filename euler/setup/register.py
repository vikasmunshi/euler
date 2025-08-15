#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Solution registry for Project Euler problems."""
from __future__ import annotations

from inspect import getsource
from pathlib import Path
from sys import modules
from types import ModuleType
from typing import Any, Callable, ParamSpec, Protocol, TypeVar, cast

from euler.setup.paths import MAX_SHARABLE, base_dir, get_module_path

__ignore_test_case_slices__: bool = False


def set_record_all_test_cases(value: bool) -> None:
    global __ignore_test_case_slices__
    __ignore_test_case_slices__ = value


PS = ParamSpec('PS')
RT = TypeVar('RT', covariant=True, )
framework_version: str = '0.2.1'


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

    @property
    def euler_problem(self) -> int: ...

    @euler_problem.setter
    def euler_problem(self, value: int) -> None: ...

    @property
    def is_private(self) -> bool: ...

    @is_private.setter
    def is_private(self, value: bool) -> None: ...

    @property
    def test_cases(self) -> list[dict[str, Any]]: ...

    @test_cases.setter
    def test_cases(self, value: list[dict[str, Any]]) -> None: ...

    @property
    def test_case_answers_file(self) -> Path: ...

    @test_case_answers_file.setter
    def test_case_answers_file(self, value: Path) -> None: ...

    @property
    def url(self) -> str: ...

    @url.setter
    def url(self, value: str) -> None: ...


FS = Callable[PS, RT]
ST = Solution[PS, RT]


def register_solution(euler_problem: int, test_cases: list[dict[str, Any]]) -> Callable[[FS], ST]:
    def wrapper(func: FS) -> ST:
        solution = cast(ST, func)
        if getattr(func, '__module__', '') == '__main__':  # Skip registering functions called directly from __main__
            return solution
        implemented_code: list[str] = getsource(func).splitlines(keepends=False)
        if 'raise NotImplementedError()' in implemented_code[2]:  # actual first line of function
            return solution  # Skip registering functions that are not yet implemented
        module: ModuleType = modules[solution.__module__]
        if not hasattr(module, 'euler_solutions_registry'):
            setattr(module, 'euler_solutions_registry', [])
        solution.euler_problem = euler_problem
        solution.is_private = euler_problem > MAX_SHARABLE
        _test_cases = getattr(module, 'test_cases', []) if __ignore_test_case_slices__ else test_cases
        for test_case in _test_cases:
            test_case['key'] = key = format_kwargs(test_case['input'])
            test_case['et_key'] = f'{solution.__name__}_{key}'
        solution.test_cases = _test_cases
        module_file: str = module.__file__ or get_module_path(euler_problem).relative_to(base_dir).as_posix()
        answers_file: Path = base_dir / module_file.replace('.py', '.json')
        solution.test_case_answers_file = answers_file
        solution.url = f'https://projecteuler.net/problem={euler_problem}'
        module.euler_solutions_registry.append(solution)
        return solution

    return wrapper


def format_kwargs(kwargs: dict[str, Any]) -> str:
    return ', '.join(sorted(f'{key}={format_val(val)}' for key, val in kwargs.items()))


def format_val(val: Any) -> str:
    if isinstance(val, int) and val % 100 == 0:
        return f'{val:.1e}'
    return f'{val}'

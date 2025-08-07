#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Solution registry for Project Euler problems."""
from __future__ import annotations

from typing import Any, Callable, ParamSpec, Protocol, TypeVar, cast

from euler.setup.test_case import MAX_SHARABLE, TestCaseCategory

__all__ = ['get_registered_solutions', 'register_solution', 'Solution', ]

PS = ParamSpec('PS')
RT = TypeVar('RT', covariant=True, )


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
    def __euler_problem__(self) -> int: ...

    @__euler_problem__.setter
    def __euler_problem__(self, value: int) -> None: ...

    @property
    def __is_private__(self) -> bool: ...

    @__is_private__.setter
    def __is_private__(self, value: bool) -> None: ...

    @property
    def __test_case_categories__(self) -> set[TestCaseCategory]: ...

    @__test_case_categories__.setter
    def __test_case_categories__(self, value: set[TestCaseCategory]) -> None: ...


FS = Callable[PS, RT]
ST = Solution[PS, RT]


def get_registered_solutions(euler_problem: int) -> list[Solution]:
    return __solutions_registry__.get(euler_problem, list())


def register_solution(euler_problem: int, test_case_category: TestCaseCategory) -> Callable[[FS], ST]:
    def wrapper(func: FS) -> ST:
        solution = cast(ST, func)
        solution.__euler_problem__ = euler_problem
        solution.__is_private__ = euler_problem > MAX_SHARABLE
        solution.__test_case_categories__ = {
            TestCaseCategory.EXTENDED: {TestCaseCategory.EXTENDED, TestCaseCategory.MAIN, TestCaseCategory.PRELIMINARY},
            test_case_category.MAIN: {TestCaseCategory.MAIN, TestCaseCategory.PRELIMINARY},
            test_case_category.PRELIMINARY: {TestCaseCategory.PRELIMINARY},
        }[test_case_category]
        if getattr(func, '__module__', '') == '__main__':  # Skip registering functions called directly from __main__
            return solution
        __solutions_registry__.setdefault(euler_problem, list()).append(solution)
        return solution

    return wrapper


__solutions_registry__: dict[int, list[Solution]] = dict()

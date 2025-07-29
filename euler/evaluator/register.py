#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" """
from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from inspect import getsource, signature
from typing import Callable, ParamSpec, TypeVar

from euler.logger import logger
from euler.setup.problems import TestCase

__all__ = ['register_solution', 'solutions', ]

solutions: dict[int, list[tuple[Callable, list[TestCase]]]] = defaultdict(list)

PS = ParamSpec("PS")  # ParamSpec to capture the parameter specification of the functions being decorated
RT = TypeVar("RT")  # TypeVar to represent the return type of the functions being decorated
FS = Callable[PS, RT]


def register_solution(*, problem_number: int, test_cases: list[TestCase]) -> Callable[[FS], FS]:
    """Register a solution function for evaluation with specified test cases. """
    test_cases = deepcopy(test_cases)

    def decorator(func: FS) -> FS:
        if 'raise NotImplementedError' in getsource(func):
            logger.info(f'Skipping, default {func.__name__} for {problem_number=}.')
        elif not test_cases:
            logger.info(f'Skipping, no test cases for {problem_number=}.')
        else:
            f_kwargs: set[str] = set(signature(func).parameters.keys())
            tc_kwargs: set[str] = set(item for items in (case.kwargs.keys() for case in test_cases) for item in items)
            if f_kwargs != tc_kwargs:
                raise TypeError(f'{problem_number=} function {func.__name__} args do not match problem args: '
                                f'{f_kwargs=} != {tc_kwargs=}')
            else:
                solutions[problem_number].append((func, test_cases,))
        return func

    return decorator

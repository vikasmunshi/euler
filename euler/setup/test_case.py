#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test Cases for Project Euler solutions."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any

from euler.logger import logger
from euler.utils.human_readable_time import human_readable_seconds, seconds_from_human_readable

MAX_SHARABLE: int = 100


class TestCaseCategory(StrEnum):
    PRELIMINARY = 'preliminary'
    MAIN = 'main'
    EXTENDED = 'extended'


@dataclass(frozen=True, kw_only=True, slots=True, eq=True, order=True)
class TestCase:
    euler_problem: int = field(compare=False, )
    kwargs: dict[str, Any] = field(default_factory=dict, compare=False, )
    result: Any = field(default=None, compare=False, )
    solution_execution_time_in_sec: dict[str, str] = field(default_factory=dict, compare=False, )
    solved: bool = field(default=False, compare=False, )
    test_case_category: TestCaseCategory = field(default=TestCaseCategory.EXTENDED, compare=False, )
    __kwargs_str__: str | None = field(init=False, repr=False, default=None, compare=False, )

    def __post_init__(self) -> None:
        if self.result is None:
            logger.warning({'euler_problem': self.euler_problem, 'kwargs': self.kwargs, 'result': self.result, })

    @property
    def kwargs_str(self) -> str:
        if self.__kwargs_str__ is None:
            __kwargs_str__: str = ', '.join(sorted(f'{key}={format_val(val)}' for key, val in self.kwargs.items()))
            object.__setattr__(self, '__kwargs_str__', __kwargs_str__)
        return self.__kwargs_str__  # type: ignore[return-value]

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop('__kwargs_str__', None)
        if self.euler_problem > MAX_SHARABLE and self.test_case_category != TestCaseCategory.PRELIMINARY:
            data['result'] = None
        data['test_case_category'] = str(self.test_case_category)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TestCase:
        if test_case_category := data.get('test_case_category'):
            data['test_case_category'] = TestCaseCategory(test_case_category)
        return cls(**data)

    def record(self, result: Any, execution_time: float, func_name: str) -> bool:
        return_value: bool = False
        if not self.solved:
            if self.result is None:
                object.__setattr__(self, 'result', result)
            object.__setattr__(self, 'solved', self.result == result)
            return_value = True
        if self.solved and self.result == result:
            previous_execution_time_str: str | None = self.solution_execution_time_in_sec.get(func_name)
            if previous_execution_time_str is None:
                previous_execution_time: float = float('inf')
            else:
                previous_execution_time = seconds_from_human_readable(previous_execution_time_str)
            if (previous_execution_time - execution_time) > 1e-2:
                self.solution_execution_time_in_sec[func_name] = human_readable_seconds(execution_time)
                return_value = True
        return return_value


def format_val(val: int | Any) -> str:
    if isinstance(val, int) and val % 100 == 0:
        return f'{val:.1e}'
    return f'{val}'

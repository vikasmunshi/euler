#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Evaluation Result Class for Project Euler problems."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=False, kw_only=True, slots=True)
class EvaluationResult:
    failed_problems: int = field(default=0)
    failed_problems_list: list[int] = field(default_factory=list)
    failed_test_cases: int = field(default=0)
    passed_problems: int = field(default=0)
    passed_problems_list: list[int] = field(default_factory=list)
    passed_test_cases: int = field(default=0)
    recorded_test_cases: int = field(default=0)
    total_execution_time_in_sec: float = field(default=0.0)
    total_problems: int = field(default=0)
    total_test_cases: int = field(default=0)
    undecided_test_cases: int = field(default=0)
    unsolved_problems: int = field(default=0)
    unsolved_problems_list: list[int] = field(default_factory=list)

    def __add__(self, other: EvaluationResult) -> EvaluationResult:
        return EvaluationResult(
                failed_problems=self.failed_problems + other.failed_problems,
                failed_problems_list=self.failed_problems_list + other.failed_problems_list,
                failed_test_cases=self.failed_test_cases + other.failed_test_cases,
                passed_problems=self.passed_problems + other.passed_problems,
                passed_test_cases=self.passed_test_cases + other.passed_test_cases,
                recorded_test_cases=self.recorded_test_cases + other.recorded_test_cases,
                total_execution_time_in_sec=self.total_execution_time_in_sec + other.total_execution_time_in_sec,
                total_problems=self.total_problems + other.total_problems,
                total_test_cases=self.total_test_cases + other.total_test_cases,
                undecided_test_cases=self.undecided_test_cases + other.undecided_test_cases,
                unsolved_problems=self.unsolved_problems + other.unsolved_problems,
                unsolved_problems_list=self.unsolved_problems_list + other.unsolved_problems_list)

    def __iadd__(self, other: EvaluationResult) -> EvaluationResult:
        self.failed_problems += other.failed_problems
        self.failed_problems_list += other.failed_problems_list
        self.failed_test_cases += other.failed_test_cases
        self.passed_problems += other.passed_problems
        self.passed_test_cases += other.passed_test_cases
        self.recorded_test_cases += other.recorded_test_cases
        self.total_execution_time_in_sec += other.total_execution_time_in_sec
        self.total_problems += other.total_problems
        self.total_test_cases += other.total_test_cases
        self.undecided_test_cases += other.undecided_test_cases
        self.unsolved_problems += other.unsolved_problems
        self.unsolved_problems_list += other.unsolved_problems_list
        return self

    def __format__(self, format_spec: str) -> str:
        if format_spec == 's' or format_spec == 'summary':
            msg = (f'{self.total_problems: 4d} problems:\n'
                   f'\t {self.passed_problems: 4d} passed,\n'
                   f'\t {self.failed_problems:4d} failed')
            if self.unsolved_problems:
                msg += f',\n\t {self.unsolved_problems: 4d} unsolved'
            msg += (f'.\n{self.total_test_cases: 4d} test cases:\n'
                    f'\t {self.passed_test_cases: 4d} passed,\n'
                    f'\t {self.failed_test_cases: 4d} failed')
            if self.undecided_test_cases:
                msg += f',\n\t {self.undecided_test_cases: 4d} undecided'
            if self.recorded_test_cases:
                msg += f',\n\t {self.recorded_test_cases: 4d} recorded'
            if self.passed_problems_list:
                msg += f'.\nSolved Problems: {list_to_ranges(self.passed_problems_list)}'
            if self.failed_problems_list:
                msg += f'.\nFailed Problems: {list_to_ranges(self.failed_problems_list)}'
            if self.unsolved_problems_list:
                msg += f'\nUnsolved Problems: {list_to_ranges(self.unsolved_problems_list)}'
            msg += f'\nTotal Execution Time: {self.total_execution_time_in_sec:.2f}s\n'
            return msg
        else:
            return f'{self}'


def list_to_ranges(numbers: list[int]) -> str:
    """Convert a list of integers to a list of ranges."""
    ranges: list[tuple[int, int]] = []
    for number in sorted(numbers):
        if not ranges or number - 1 != ranges[-1][1]:
            ranges.append((number, number))
        else:
            ranges[-1] = (ranges[-1][0], number)
    return ', '.join(f'{start}..{end}' if start != end else str(start) for start, end in ranges)

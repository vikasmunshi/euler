#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 1: Multiples of 3 or 5.

Problem Statement:
    If we list all the natural numbers below 10 that are multiples of 3 or 5, we
    get 3, 5, 6 and 9. The sum of these multiples is 23.

    Find the sum of all the multiples of 3 or 5 below 1000.

Solution Approach:
    Use inclusion–exclusion principle. Sum multiples of 3 and 5, then subtract multiples
    of 15 to avoid double counting. Employ arithmetic progression sums for constant time.

Answer: 233168
URL: https://projecteuler.net/problem=1
"""
from __future__ import annotations

from typing import Any, Generator

from euler_solver.framework import evaluate, logger, register_solution

euler_problem: int = 1
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': 23},
    {'category': 'main', 'input': {'max_limit': 1000}, 'answer': 233168},
    {'category': 'extra', 'input': {'max_limit': 1000000000}, 'answer': 233333333166666668},
]


def sum_arithmetic_series(common_difference: int, *, max_limit: int) -> int:
    n = (max_limit - 1) // common_difference
    return common_difference * (n * (n + 1)) // 2


def generate_arithmetic_series_range(common_difference: int, *, max_limit: int) -> Generator[int, None, None]:
    for term in range(0, max_limit, common_difference):
        yield term


def generate_arithmetic_series_loop(common_difference: int, *, max_limit: int) -> Generator[int, None, None]:
    term: int = 0
    while term < max_limit:
        yield term
        term += common_difference


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_multiples_of_3_or_5_p0001_s0(*, max_limit: int) -> int:
    return (sum_arithmetic_series(3, max_limit=max_limit)
            + sum_arithmetic_series(5, max_limit=max_limit)
            - sum_arithmetic_series(15, max_limit=max_limit))


@register_solution(euler_problem=euler_problem, max_test_case_index=2)
def solve_multiples_of_3_or_5_p0001_s1(*, max_limit: int) -> int:
    result: int = 0
    for term in range(0, max_limit):
        if term % 3 == 0 or term % 5 == 0:
            result += term
    return result


@register_solution(euler_problem=euler_problem, max_test_case_index=2)
def solve_multiples_of_3_or_5_p0001_s2(*, max_limit: int) -> int:
    return (sum(range(0, max_limit, 3))
            + sum(range(0, max_limit, 5))
            - sum(range(0, max_limit, 15)))


@register_solution(euler_problem=euler_problem, max_test_case_index=2)
def solve_multiples_of_3_or_5_p0001_s3(*, max_limit: int) -> int:
    return (sum(generate_arithmetic_series_range(3, max_limit=max_limit))
            + sum(generate_arithmetic_series_range(5, max_limit=max_limit))
            - sum(generate_arithmetic_series_range(15, max_limit=max_limit)))


@register_solution(euler_problem=euler_problem, max_test_case_index=2)
def solve_multiples_of_3_or_5_p0001_s4(*, max_limit: int) -> int:
    return (sum(generate_arithmetic_series_loop(3, max_limit=max_limit))
            + sum(generate_arithmetic_series_loop(5, max_limit=max_limit))
            - sum(generate_arithmetic_series_loop(15, max_limit=max_limit)))


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

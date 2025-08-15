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

Answer: TBD
URL: https://projecteuler.net/problem=1
"""
from __future__ import annotations

from typing import Any, Generator

from euler.logger import logger
from euler.setup import evaluate, register_solution

euler_problem: int = 1
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'preliminary', 'input': {'max_limit': 10}},
    {'category': 'main', 'input': {'max_limit': 1000}},
    {'category': 'extended', 'input': {'max_limit': 1000000000}}
]


def sum_arithmetic_series(common_difference: int, *, max_limit: int) -> int:
    ...


def generate_arithmetic_series_range(common_difference: int, *, max_limit: int) -> Generator[int, None, None]:
    ...


def generate_arithmetic_series_loop(common_difference: int, *, max_limit: int) -> Generator[int, None, None]:
    ...


@register_solution(euler_problem=euler_problem, test_cases=test_cases[:])
def solve_multiples_of_3_or_5_p0001_s0(*, max_limit: int) -> int:
    ...


@register_solution(euler_problem=euler_problem, test_cases=test_cases[:2])
def solve_multiples_of_3_or_5_p0001_s1(*, max_limit: int) -> int:
    ...


@register_solution(euler_problem=euler_problem, test_cases=test_cases[:2])
def solve_multiples_of_3_or_5_p0001_s2(*, max_limit: int) -> int:
    ...


@register_solution(euler_problem=euler_problem, test_cases=test_cases[:2])
def solve_multiples_of_3_or_5_p0001_s3(*, max_limit: int) -> int:
    ...


@register_solution(euler_problem=euler_problem, test_cases=test_cases[:2])
def solve_multiples_of_3_or_5_p0001_s4(*, max_limit: int) -> int:
    ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))

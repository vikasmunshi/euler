#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 20: Factorial Digit Sum.

Problem Statement:
    n! means n × (n - 1) × ⋯ × 3 × 2 × 1.

    For example, 10! = 10 × 9 × ⋯ × 3 × 2 × 1 = 3628800,
    and the sum of the digits in the number 10! is 3 + 6 + 2 + 8 + 8 + 0 + 0 = 27.

    Find the sum of the digits in the number 100!.

Solution Approach:
    Use factorial calculation from number theory.
    Convert the factorial result to string and sum its digits.
    Efficient Python arbitrary precision integers allow direct computation.
    Time complexity depends mainly on the multiplication cost for 100!.
    Digit summation is O(digits), feasible for given input.

Answer: ...
URL: https://projecteuler.net/problem=20
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 20
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'preliminary', 'input': {'n': 10}},
    {'category': 'main', 'input': {'n': 100}}
]


@register_solution(euler_problem=euler_problem, max_test_case=None)
def solve_factorial_digit_sum_p0020_s0(*, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))

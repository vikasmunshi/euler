#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 401: Sum of Squares of Divisors.

Problem Statement:
    The divisors of 6 are 1, 2, 3 and 6.
    The sum of the squares of these numbers is 1+4+9+36=50.

    Let sigma_2(n) represent the sum of the squares of the divisors of n.
    Thus sigma_2(6)=50.

    Let SIGMA_2 represent the summatory function of sigma_2, that is
    SIGMA_2(n) = sum of sigma_2(i) for i=1 to n.
    The first 6 values of SIGMA_2 are: 1, 6, 16, 37, 63 and 113.

    Find SIGMA_2(10^15) modulo 10^9.

Solution Approach:
    Use number theory and divisor function properties.
    Use formula for sum of squares of divisors leveraging multiplicative functions.
    Employ fast summation techniques for summatory functions up to large n.
    Modular arithmetic is critical. Expected complexity O(n^(2/3)) or better.

Answer: ...
URL: https://projecteuler.net/problem=401
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 401
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_sum_of_squares_of_divisors_p0401_s0() -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
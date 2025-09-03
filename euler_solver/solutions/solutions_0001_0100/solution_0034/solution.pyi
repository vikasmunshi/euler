#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 34: Digit Factorials.

Problem Statement:
    145 is a curious number, as 1! + 4! + 5! = 1 + 24 + 120 = 145.

    Find the sum of all numbers which are equal to the sum of the factorial of their digits.

    Note: As 1! = 1 and 2! = 2 are not sums they are not included.

Solution Approach:
    Use precomputed factorials for digits 0-9 for quick lookup.
    Enumerate numbers up to a certain limit (determined by the maximal digit factorial sums).
    Check each number if it equals the sum of the factorial of its digits.
    Sum all such numbers excluding 1 and 2.
    Use combinatorics and bounding arguments for efficient upper bound estimation.
    Expected complexity is manageable with direct enumeration and pruning.

Answer: ...
URL: https://projecteuler.net/problem=34
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 34
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}}
]


@register_solution(euler_problem=euler_problem, max_test_case=None)
def solve_digit_factorials_p0034_s0() -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))

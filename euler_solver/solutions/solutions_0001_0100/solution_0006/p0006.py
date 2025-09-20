#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 6: Sum Square Difference.

Problem Statement:
    The sum of the squares of the first ten natural numbers is,
    1^2 + 2^2 + ... + 10^2 = 385.
    The square of the sum of the first ten natural numbers is,
    (1 + 2 + ... + 10)^2 = 55^2 = 3025.
    Hence the difference between the sum of the squares of the first ten natural
    numbers and the square of the sum is 3025 - 385 = 2640.

    Find the difference between the sum of the squares of the first one hundred
    natural numbers and the square of the sum.

Solution Approach:
    Use mathematical formulas for sums of integers and sums of squares:
        Sum of first n natural numbers: n(n+1)/2
        Sum of squares of first n natural numbers: n(n+1)(2n+1)/6
    Compute square of sum and sum of squares separately, then take the difference.
    Time complexity is O(1) as this uses direct formulas.

Answer: 25164150
URL: https://projecteuler.net/problem=6
"""
from __future__ import annotations

from typing import Any

from euler_solver.framework import evaluate, logger, register_solution

euler_problem: int = 6
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 10}, 'answer': 2640},
    {'category': 'main', 'input': {'n': 100}, 'answer': 25164150},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_sum_square_difference_p0006_s0(*, n: int) -> int:
    return (n * (n + 1) // 2) ** 2 - (2 * n + 1) * (n + 1) * n // 6


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

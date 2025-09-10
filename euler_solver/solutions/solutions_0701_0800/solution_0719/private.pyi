#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 719: Number Splitting.

Problem Statement:
    We define an S-number to be a natural number, n, that is a perfect square and
    its square root can be obtained by splitting the decimal representation of n
    into 2 or more numbers then adding the numbers.

    For example, 81 is an S-number because sqrt(81) = 8 + 1.
    6724 is an S-number: sqrt(6724) = 6 + 72 + 4.
    8281 is an S-number: sqrt(8281) = 8 + 2 + 81 = 82 + 8 + 1.
    9801 is an S-number: sqrt(9801) = 98 + 0 + 1.

    Further we define T(N) to be the sum of all S numbers n ≤ N. You are given
    T(10^4) = 41333.

    Find T(10^12).

Solution Approach:
    Use digit dynamic programming or backtracking with memoization over the digits
    of the square numbers.
    Enumerate perfect squares up to 10^12 and attempt to split their decimal form
    into parts summing to the square root.
    Key ideas: combinatorics on digits, perfect squares, efficient string splits,
    memoization.
    Time complexity must be optimized via pruning and caching partial sums.

Answer: ...
URL: https://projecteuler.net/problem=719
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 719
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10000}},
    {'category': 'main', 'input': {'max_limit': 1000000000000}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_number_splitting_p0719_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 152: Sums of Square Reciprocals.

Problem Statement:
    There are several ways to write the number 1/2 as a sum of square
    reciprocals using distinct integers.

    For instance, the numbers {2, 3, 4, 5, 7, 12, 15, 20, 28, 35} can be used:

    1/2 = 1/2^2 + 1/3^2 + 1/4^2 + 1/5^2 +
         1/7^2 + 1/12^2 + 1/15^2 + 1/20^2 +
         1/28^2 + 1/35^2

    In fact, only using integers between 2 and 45 inclusive, there are exactly
    three ways to do it, the remaining two being:
    {2, 3, 4, 6, 7, 9, 10, 20, 28, 35, 36, 45} and
    {2, 3, 4, 6, 7, 9, 12, 15, 28, 30, 35, 36, 45}.

    How many ways are there to write 1/2 as a sum of reciprocals of squares
    using distinct integers between 2 and 80 inclusive?

Solution Approach:
    Use exact rational arithmetic (fractions) to avoid floating-point error.
    Precompute reciprocal squares r_k = 1/k^2 for k in [2..max_limit].
    Use depth-first search (subset-sum style) with strong pruning:
        - Sort terms (e.g., descending) and use prefix sums to bound remaining sum.
        - Backtrack and skip branches where remaining max sum < target or current
          sum > target.
    Optionally use meet-in-the-middle: split range, enumerate possible sums on
    each side, then count complementary pairs. Expect exponential worst-case
    time but heavy pruning makes max_limit=80 feasible in optimized code.

Answer: ...
URL: https://projecteuler.net/problem=152
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 152
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 45}},
    {'category': 'main', 'input': {'max_limit': 80}},
    {'category': 'extra', 'input': {'max_limit': 100}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_sums_of_square_reciprocals_p0152_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 817: Digits in Squares.

Problem Statement:
    Define m = M(n, d) to be the smallest positive integer such that when m^2 is written
    in base n it includes the base n digit d. For example, M(10,7) = 24 because if all the
    squares are written out in base 10 the first time the digit 7 occurs is in 24^2 = 576.
    M(11,10) = 19 as 19^2 = 361 = 2A9_11.

    Find the sum from d = 1 to 10^5 of M(p, p - d) where p = 10^9 + 7.

Solution Approach:
    Use number theory and properties of modular arithmetic. Efficient base-n digit checks
    combined with fast search for minimal m are needed. The large prime base and huge sum
    limit require carefully optimized algorithms, possibly caching or mathematical insights.
    Expect O((10^5) * log computations) with pruning and digit presence checks.

Answer: ...
URL: https://projecteuler.net/problem=817
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 817
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_digits_in_squares_p0817_s0() -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
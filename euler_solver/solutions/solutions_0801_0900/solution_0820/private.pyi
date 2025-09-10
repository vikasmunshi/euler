#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 820: Nth Digit of Reciprocals.

Problem Statement:
    Let d_n(x) be the nth decimal digit of the fractional part of x, or 0 if the fractional
    part has fewer than n digits.

    For example:
        d_7(1) = d_7(1/2) = d_7(1/4) = d_7(1/5) = 0
        d_7(1/3) = 3 since 1/3 = 0.3333333...
        d_7(1/6) = 6 since 1/6 = 0.1666666...
        d_7(1/7) = 1 since 1/7 = 0.1428571...

    Let S(n) = sum from k=1 to n of d_n(1/k).

    You are given:
        S(7) = 0 + 0 + 3 + 0 + 0 + 6 + 1 = 10
        S(100) = 418

    Find S(10^7).

Solution Approach:
    Analyze decimal expansions of reciprocals 1/k focusing on the nth digit of their
    fractional parts. Use number theory to efficiently extract digits at large n without
    full decimal expansion, possibly involving modular arithmetic and cycle detection.
    Avoid direct floating-point computation for large n. Expect O(n log n) or better with
    optimized techniques.

Answer: ...
URL: https://projecteuler.net/problem=820
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 820
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 7}},
    {'category': 'main', 'input': {'n': 10000000}},
]

@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_nth_digit_of_reciprocals_p0820_s0(*, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
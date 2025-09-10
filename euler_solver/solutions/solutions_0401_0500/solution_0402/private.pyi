#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 402: Integer-valued Polynomials.

Problem Statement:
    It can be shown that the polynomial n^4 + 4n^3 + 2n^2 + 5n is a multiple of 6 for every
    integer n. It can also be shown that 6 is the largest integer satisfying this property.

    Define M(a, b, c) as the maximum m such that n^4 + an^3 + bn^2 + cn is a multiple of m
    for all integers n. For example, M(4, 2, 5) = 6.

    Also, define S(N) as the sum of M(a, b, c) for all 0 < a, b, c ≤ N.

    We can verify that S(10) = 1972 and S(10000) = 2024258331114.

    Let F_k be the Fibonacci sequence:
    F_0 = 0, F_1 = 1 and
    F_k = F_{k-1} + F_{k-2} for k ≥ 2.

    Find the last 9 digits of the sum of S(F_k) for 2 ≤ k ≤ 1234567890123.

Solution Approach:
    Use number theory and polynomial divisibility properties to characterize M(a,b,c).
    Exploit recurrence and algebraic structure in Fibonacci indices and modulo arithmetic.
    Handle large Fibonacci indices with fast doubling and modular arithmetic.
    Use efficient summation and caching. Time complexity depends on fast Fibonacci and divisor sums.

Answer: ...
URL: https://projecteuler.net/problem=402
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 402
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'k_start': 2, 'k_end': 1234567890123}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_integer_valued_polynomials_p0402_s0(*, k_start: int, k_end: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
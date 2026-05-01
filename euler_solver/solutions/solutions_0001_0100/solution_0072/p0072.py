#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 72: Counting Fractions.

Problem Statement:
    Consider the fraction, n/d, where n and d are positive integers. If n < d and
    HCF(n,d) = 1, it is called a reduced proper fraction.

    If we list the set of reduced proper fractions for d ≤ 8 in ascending order of
    size, we get:
    1/8, 1/7, 1/6, 1/5, 1/4, 2/7, 1/3, 3/8, 2/5, 3/7, 1/2, 4/7, 3/5, 5/8, 2/3,
    5/7, 3/4, 4/5, 5/6, 6/7, 7/8

    It can be seen that there are 21 elements in this set.

    How many elements would be contained in the set of reduced proper fractions for
    d ≤ 1000000?

Solution Approach:
    Use number theory, specifically Euler's Totient function φ(d), which counts the
    positive integers up to d that are relatively prime to d.

    The answer is the sum of φ(d) for d from 2 to the given limit.

    Efficient computation can use a sieve-like algorithm akin to the Sieve of
    Eratosthenes to compute φ values for all d ≤ limit in O(n log log n) time.

Answer: 303963552391
URL: https://projecteuler.net/problem=72
"""
from __future__ import annotations

from typing import Any, List

from euler_solver.framework import evaluate, logger, register_solution

euler_problem: int = 72
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_d': 8}, 'answer': 21},
    {'category': 'dev', 'input': {'max_d': 10}, 'answer': 31},
    {'category': 'dev', 'input': {'max_d': 100}, 'answer': 3043},
    {'category': 'dev', 'input': {'max_d': 1000}, 'answer': 304191},
    {'category': 'dev', 'input': {'max_d': 10000}, 'answer': 30397485},
    {'category': 'dev', 'input': {'max_d': 100000}, 'answer': 3039650753},
    {'category': 'main', 'input': {'max_d': 1000000}, 'answer': 303963552391},
    {'category': 'extra', 'input': {'max_d': 10000000}, 'answer': 30396356427241},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_counting_fractions_p0072_s0(*, max_d: int) -> int:
    euler_totients: List[int] = list(range(max_d + 1))
    result: int = 0
    for n in range(2, max_d + 1):
        if euler_totients[n] == n:
            for j in range(n, max_d + 1, n):
                euler_totients[j] = euler_totients[j] // n * (n - 1)
        result += euler_totients[n]
    return result


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

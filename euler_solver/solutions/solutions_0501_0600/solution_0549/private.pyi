#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 549: Divisibility of Factorials.

Problem Statement:
    The smallest number m such that 10 divides m! is m=5.
    The smallest number m such that 25 divides m! is m=10.

    Let s(n) be the smallest number m such that n divides m!.
    So s(10)=5 and s(25)=10.
    Let S(n) be the sum of s(i) for 2 <= i <= n.
    S(100)=2012.

    Find S(10^8).

Solution Approach:
    Use number theory and prime factorization to determine s(n) efficiently.
    For each i, s(i) is the minimum m such that the prime factors of i with
    their multiplicities divide m! (factorial).
    This reduces to calculating the smallest m such that the sum of floor(m/p^k)
    for all k is at least the exponent of prime p in i.
    Utilize prime sieve and binary search per prime factor for efficiency.
    Aggregation over all i up to 10^8 needs careful optimization and caching.
    Expect time complexity near O(n log n) or optimized via segmented methods.

Answer: ...
URL: https://projecteuler.net/problem=549
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 549
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_divisibility_of_factorials_p0549_s0() -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
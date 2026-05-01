#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 242: Odd Triplets.

Problem Statement:
    Given the set {1,2,...,n}, we define f(n, k) as the number of its k-element
    subsets with an odd sum of elements. For example, f(5,3) = 4, since the set
    {1,2,3,4,5} has four 3-element subsets having an odd sum: {1,2,4},
    {1,3,5}, {2,3,4} and {2,4,5}.

    When all three values n, k and f(n, k) are odd, we say that they make an
    odd-triplet [n, k, f(n, k)].

    There are exactly five odd-triplets with n <= 10, namely:
    [1,1,f(1,1) = 1], [5,1,f(5,1) = 3], [5,5,f(5,5) = 1],
    [9,1,f(9,1) = 5] and [9,9,f(9,9) = 1].

    How many odd-triplets are there with n <= 10^12?

URL: https://projecteuler.net/problem=242
"""
from typing import Any

euler_problem: int = 242
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'ZFruHQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

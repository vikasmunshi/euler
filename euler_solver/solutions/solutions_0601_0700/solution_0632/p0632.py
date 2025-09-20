#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 632: Square Prime Factors.

Problem Statement:
    For an integer n, we define the square prime factors of n to be the primes
    whose square divides n. For example, the square prime factors of 1500 =
    2^2 × 3 × 5^3 are 2 and 5.

    Let C_k(N) be the number of integers between 1 and N inclusive with exactly
    k square prime factors. You are given some values of C_k(N) in the following
    table:

        k =      0        1        2        3        4        5
    N=10       7        3        0        0        0        0
    N=10^2     61       36       3        0        0        0
    N=10^3     608      343      48       1        0        0
    N=10^4     6083     3363     533      21       0        0
    N=10^5     60794    33562    5345     297      2        0
    N=10^6     607926   335438   53358    3218     60       0
    N=10^7     6079291  3353956  533140   32777    834      2
    N=10^8     60792694 33539196 5329747  329028   9257     78

    Find the product of all non-zero C_k(10^16). Give the result reduced modulo
    1,000,000,007.

URL: https://projecteuler.net/problem=632
"""
from typing import Any

euler_problem: int = 632
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'max_limit': 10000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

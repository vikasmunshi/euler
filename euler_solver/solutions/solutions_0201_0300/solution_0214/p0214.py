#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 214: Totient Chains.

Problem Statement:
    Let phi be Euler's totient function, i.e. for a natural number n, phi(n)
    is the number of k, 1 <= k <= n, for which gcd(k, n) = 1.

    By iterating phi, each positive integer generates a decreasing chain of
    numbers ending in 1.
    E.g. if we start with 5 the sequence 5,4,2,1 is generated.
    Here is a listing of all chains with length 4:
    5,4,2,1
    7,6,2,1
    8,4,2,1
    9,6,2,1
    10,4,2,1
    12,4,2,1
    14,6,2,1
    18,6,2,1

    Only two of these chains start with a prime, their sum is 12.

    What is the sum of all primes less than 40000000 which generate a chain
    of length 25?

URL: https://projecteuler.net/problem=214
"""
from typing import Any

euler_problem: int = 214
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 40000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 100000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

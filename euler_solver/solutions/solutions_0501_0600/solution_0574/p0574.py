#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 574: Verifying Primes.

Problem Statement:
    Let q be a prime and A ≥ B >0 be two integers with the following properties:

        A and B have no prime factor in common, that is gcd(A,B)=1.
        The product AB is divisible by every prime less than q.

    It can be shown that, given these conditions, any sum A+B < q² and any difference
    1 < A-B < q² has to be a prime number. Thus you can verify that a number p is prime
    by showing that either p = A+B < q² or p = A-B < q² for some A,B,q fulfilling the
    conditions listed above.

    Let V(p) be the smallest possible value of A in any sum p = A+B and any difference
    p = A-B that verifies p being prime. Examples:
        V(2) = 1, since 2 = 1 + 1 < 2².
        V(37) = 22, since 37 = 22 + 15 = 2 ⋅ 11 + 3 ⋅ 5 < 7² is the associated sum with
        the smallest possible A.
        V(151) = 165 since 151 = 165 - 14 = 3 ⋅ 5 ⋅ 11 - 2 ⋅ 7 < 13² is the associated
        difference with the smallest possible A.

    Let S(n) be the sum of V(p) for all primes p < n. For example, S(10) = 10 and
    S(200) = 7177.

    Find S(3800).

URL: https://projecteuler.net/problem=574
"""
from typing import Any

euler_problem: int = 574
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 3800}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 10000}, 'answer': None},
]
encrypted: str = (
    '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'
    'Yg15D5Lj4T02uzE1'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

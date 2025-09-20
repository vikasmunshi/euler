#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 552: Chinese Leftovers II.

Problem Statement:
    Let A_n be the smallest positive integer satisfying A_n mod p_i = i for all 1 <= i <= n,
    where p_i is the i-th prime.

    For example A_2 = 5, since this is the smallest positive solution of the system of equations
        A_2 mod 2 = 1
        A_2 mod 3 = 2

    The system of equations for A_3 adds another constraint. That is, A_3 is the smallest positive
    solution of
        A_3 mod 2 = 1
        A_3 mod 3 = 2
        A_3 mod 5 = 3

    and hence A_3 = 23. Similarly, one gets A_4 = 53 and A_5 = 1523.

    Let S(n) be the sum of all primes up to n that divide at least one element in the sequence A.
    For example, S(50) = 69 = 5 + 23 + 41, since 5 divides A_2, 23 divides A_3 and 41 divides
    A_10 = 5765999453. No other prime number up to 50 divides an element in A.

    Find S(300000).

URL: https://projecteuler.net/problem=552
"""
from typing import Any

euler_problem: int = 552
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 50}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 300000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

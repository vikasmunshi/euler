#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 347: Largest Integer Divisible by Two Primes.

Problem Statement:
    The largest integer <= 100 that is only divisible by both the primes 2
    and 3 is 96, as 96 = 32 * 3 = 2^5 * 3. For two distinct primes p and q
    let M(p, q, N) be the largest positive integer <= N only divisible by
    both p and q and M(p, q, N) = 0 if such a positive integer does not exist.
    E.g. M(2, 3, 100) = 96.
    M(3, 5, 100) = 75 and not 90 because 90 is divisible by 2, 3 and 5.
    Also M(2, 73, 100) = 0 because there does not exist a positive integer <=
    100 that is divisible by both 2 and 73.
    Let S(N) be the sum of all distinct M(p, q, N). S(100) = 2262.
    Find S(10000000).

URL: https://projecteuler.net/problem=347
"""
from typing import Any

euler_problem: int = 347
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
    '5XvYpwXs20AxdppT'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

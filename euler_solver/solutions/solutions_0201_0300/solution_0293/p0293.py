#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 293: Pseudo-Fortunate Numbers.

Problem Statement:
    An even positive integer N is called admissible if it is a power of 2 or
    if its distinct prime factors are consecutive primes.
    The first twelve admissible numbers are 2, 4, 6, 8, 12, 16, 18, 24, 30, 32,
    36, 48.

    If N is admissible, the smallest integer M > 1 such that N+M is prime is
    called the pseudo-Fortunate number for N.

    For example, N = 630 is admissible since it is even and its distinct prime
    factors are the consecutive primes 2, 3, 5 and 7. The next prime after 631
    is 641, hence the pseudo-Fortunate number for 630 is M = 11. The
    pseudo-Fortunate number for 16 is 3.

    Find the sum of all distinct pseudo-Fortunate numbers for admissible
    numbers N less than 10^9.

URL: https://projecteuler.net/problem=293
"""
from typing import Any

euler_problem: int = 293
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'TTj0EdwZZCNuKw9fOVTcWg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

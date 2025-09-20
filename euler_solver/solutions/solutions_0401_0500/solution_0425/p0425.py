#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 425: Prime Connection.

Problem Statement:
    Two positive numbers A and B are said to be connected (denoted by "A <-> B") if one of these
    conditions holds:
    (1) A and B have the same length and differ in exactly one digit; for example, 123 <-> 173.
    (2) Adding one digit to the left of A (or B) makes B (or A); for example, 23 <-> 223 and 123 <-> 23.

    We call a prime P a 2's relative if there exists a chain of connected primes between 2 and P and
    no prime in the chain exceeds P.

    For example, 127 is a 2's relative. One of the possible chains is shown below:
    2 <-> 3 <-> 13 <-> 113 <-> 103 <-> 107 <-> 127
    However, 11 and 103 are not 2's relatives.

    Let F(N) be the sum of the primes ≤ N which are not 2's relatives.
    We can verify that F(10^3) = 431 and F(10^4) = 78728.

    Find F(10^7).

URL: https://projecteuler.net/problem=425
"""
from typing import Any

euler_problem: int = 425
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

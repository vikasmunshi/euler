#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 429: Sum of Squares of Unitary Divisors.

Problem Statement:
    A unitary divisor d of a number n is a divisor of n that has the property gcd(d, n/d) = 1.
    The unitary divisors of 4! = 24 are 1, 3, 8 and 24.
    The sum of their squares is 1^2 + 3^2 + 8^2 + 24^2 = 650.

    Let S(n) represent the sum of the squares of the unitary divisors of n. Thus S(4!) = 650.

    Find S(100000000!) modulo 1000000009.

URL: https://projecteuler.net/problem=429
"""
from typing import Any

euler_problem: int = 429
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 100000000, 'modulo': 1000000009}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

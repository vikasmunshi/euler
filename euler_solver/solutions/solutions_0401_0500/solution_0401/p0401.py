#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 401: Sum of Squares of Divisors.

Problem Statement:
    The divisors of 6 are 1, 2, 3 and 6.
    The sum of the squares of these numbers is 1+4+9+36=50.

    Let sigma_2(n) represent the sum of the squares of the divisors of n.
    Thus sigma_2(6)=50.

    Let SIGMA_2 represent the summatory function of sigma_2, that is
    SIGMA_2(n) = sum of sigma_2(i) for i=1 to n.
    The first 6 values of SIGMA_2 are: 1, 6, 16, 37, 63 and 113.

    Find SIGMA_2(10^15) modulo 10^9.

URL: https://projecteuler.net/problem=401
"""
from typing import Any

euler_problem: int = 401
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'VP6TnhsrTJJFHrDOwnsgzM+mubMAQ6noUJxdIQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 650: Divisors of Binomial Product.

Problem Statement:
    Let B(n) = product from k=0 to n of n choose k, a product of binomial coefficients.
    For example, B(5) = 1 × 5 × 10 × 10 × 5 × 1 = 2500.

    Let D(n) = sum of the divisors of B(n).
    For example, the divisors of B(5) are 1, 2, 4, 5, 10, 20, 25, 50, 100, 125, 250, 500,
    625, 1250 and 2500, so D(5) = 5467.

    Let S(n) = sum from k=1 to n of D(k).
    Given S(5) = 5736, S(10) = 141740594713218418, and S(100) mod 1000000007 = 332792866.

    Find S(20000) mod 1000000007.

URL: https://projecteuler.net/problem=650
"""
from typing import Any

euler_problem: int = 650
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 5}, 'answer': None},
    {'category': 'main', 'input': {'n': 20000}, 'answer': None},
    {'category': 'extra', 'input': {'n': 100000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

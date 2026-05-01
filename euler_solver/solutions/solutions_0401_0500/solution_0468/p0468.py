#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 468: Smooth Divisors of Binomial Coefficients.

Problem Statement:
    An integer is called B-smooth if none of its prime factors is greater than B.

    Let S_B(n) be the largest B-smooth divisor of n.
    Examples:
        S_1(10) = 1
        S_4(2100) = 12
        S_17(2496144) = 5712

    Define F(n) = sum_{B=1}^n sum_{r=0}^n S_B(binomial(n, r)), where binomial(n, r) denotes
    the binomial coefficient.
    Examples:
        F(11) = 3132
        F(1111) mod 1,000,000,993 = 706036312
        F(111,111) mod 1,000,000,993 = 22156169

    Find F(11,111,111) mod 1,000,000,993.

URL: https://projecteuler.net/problem=468
"""
from typing import Any

euler_problem: int = 468
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 11}, 'answer': None},
    {'category': 'main', 'input': {'n': 11111111}, 'answer': None},
    {'category': 'extra', 'input': {'n': 111111111}, 'answer': None},
]
encrypted: str = (
    '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'
    'A2lPRodREKe5UEAyA5tQsKdi5qUMVyYu'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

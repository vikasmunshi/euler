#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 231: Prime Factorisation of Binomial Coefficients.

Problem Statement:
    The binomial coefficient C(10, 3) = 120.
    120 = 2^3 * 3 * 5 = 2 * 2 * 2 * 3 * 5, and 2 + 2 + 2 + 3 + 5 = 14.
    So the sum of the terms in the prime factorisation of C(10, 3) is 14.

    Find the sum of the terms in the prime factorisation of C(20000000, 15000000).

URL: https://projecteuler.net/problem=231
"""
from typing import Any

euler_problem: int = 231
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 10, 'k': 3}, 'answer': None},
    {'category': 'main', 'input': {'n': 20000000, 'k': 15000000}, 'answer': None},
]
encrypted: str = (
    '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'
    '53JSQMg+wEebWoA8sAJgrg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

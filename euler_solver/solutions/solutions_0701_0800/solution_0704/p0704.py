#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 704: Factors of Two in Binomial Coefficients.

Problem Statement:
    Define g(n, m) to be the largest integer k such that 2^k divides the binomial
    coefficient C(n, m). For example, C(12, 5) = 792 = 2^3 * 3^2 * 11, so g(12, 5) = 3.
    Then define F(n) = max { g(n, m) : 0 ≤ m ≤ n }. Given that F(10) = 3 and F(100) = 6.

    Let S(N) = sum from n=1 to N of F(n). It is given that S(100) = 389 and S(10^7) = 203222840.

    Find S(10^16).

URL: https://projecteuler.net/problem=704
"""
from typing import Any

euler_problem: int = 704
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'kpkUTK1Cvop2ueX8'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

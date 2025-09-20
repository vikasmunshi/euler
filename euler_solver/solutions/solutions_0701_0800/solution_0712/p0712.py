#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 712: Exponent Difference.

Problem Statement:
    For any integer n > 0 and prime number p, define ν_p(n) as the greatest integer r
    such that p^r divides n.

    Define D(n, m) = sum over primes p of |ν_p(n) - ν_p(m)|. For example, D(14,24) = 4.

    Furthermore, define S(N) = sum over 1 ≤ n, m ≤ N of D(n, m). You are given S(10) = 210
    and S(10^2) = 37018.

    Find S(10^12). Give your answer modulo 1,000,000,007.

URL: https://projecteuler.net/problem=712
"""
from typing import Any

euler_problem: int = 712
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 515: Dissonant Numbers.

Problem Statement:
    Let d(p, n, 0) be the multiplicative inverse of n modulo prime p, defined as
    n × d(p, n, 0) = 1 mod p.
    Let d(p, n, k) = sum for i = 1 to n of d(p, i, k - 1) for k ≥ 1.
    Let D(a, b, k) = sum of (d(p, p-1, k) mod p) for all primes p with a ≤ p < a + b.

    You are given:
        D(101, 1, 10) = 45
        D(10^3, 10^2, 10^2) = 8334
        D(10^6, 10^3, 10^3) = 38162302

    Find D(10^9, 10^5, 10^5).

URL: https://projecteuler.net/problem=515
"""
from typing import Any

euler_problem: int = 515
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'a': 101, 'b': 1, 'k': 10}, 'answer': None},
    {'category': 'main', 'input': {'a': 1000000000, 'b': 100000, 'k': 100000}, 'answer': None},
]
encrypted: str = (
    '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'
    '4nu1GFVLOU4ebPu86B/wZRjP0ZmuqaCC'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

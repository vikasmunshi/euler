#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 489: Common Factors Between Two Sequences.

Problem Statement:
    Let G(a, b) be the smallest non-negative integer n for which gcd(n^3 + b, (n + a)^3
    + b) is maximized.
    For example, G(1, 1) = 5 because gcd(n^3 + 1, (n + 1)^3 + 1) reaches its maximum value
    of 7 for n = 5, and is smaller for 0 <= n < 5.
    Let H(m, n) = sum of G(a, b) for 1 <= a <= m, 1 <= b <= n.
    You are given H(5, 5) = 128878 and H(10, 10) = 32936544.

    Find H(18, 1900).

URL: https://projecteuler.net/problem=489
"""
from typing import Any

euler_problem: int = 489
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'m': 5, 'n': 5}, 'answer': None},
    {'category': 'main', 'input': {'m': 18, 'n': 1900}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 531: Chinese Leftovers.

Problem Statement:
    Let g(a, n, b, m) be the smallest non-negative solution x to the system:
    x = a mod n
    x = b mod m
    if such a solution exists, otherwise 0.

    E.g. g(2,4,4,6) = 10, but g(3,4,4,6) = 0.

    Let φ(n) be Euler's totient function.

    Let f(n, m) = g(φ(n), n, φ(m), m).

    Find the sum of f(n, m) for 1000000 <= n < m < 1005000.

URL: https://projecteuler.net/problem=531
"""
from typing import Any

euler_problem: int = 531
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'start': 1000000, 'end': 1005000}, 'answer': None},
]
encrypted: str = (
    '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'
    '7WJj2cjIrfiOQFvfU5oXWBrfRArNhClO'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

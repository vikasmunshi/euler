#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 484: Arithmetic Derivative.

Problem Statement:
    The arithmetic derivative is defined by

        p' = 1 for any prime p
        (ab)' = a'b + ab' for all integers a, b (Leibniz rule)

    For example, 20' = 24.

    Find the sum gcd(k, k') for 1 < k ≤ 5 × 10^15.

    Note: gcd(x,y) denotes the greatest common divisor of x and y.

URL: https://projecteuler.net/problem=484
"""
from typing import Any

euler_problem: int = 484
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'max_limit': 5000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'x/DxiKNGLRQ='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

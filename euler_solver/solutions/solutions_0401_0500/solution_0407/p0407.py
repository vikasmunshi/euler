#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 407: Idempotents.

Problem Statement:
    If we calculate a^2 mod 6 for 0 <= a <= 5 we get: 0, 1, 4, 3, 4, 1.
    The largest value of a such that a^2 ≡ a (mod 6) is 4.
    Let M(n) be the largest value of a < n such that a^2 ≡ a (mod n).
    So M(6) = 4.

    Find the sum of M(n) for 1 <= n <= 10^7.

URL: https://projecteuler.net/problem=407
"""
from typing import Any

euler_problem: int = 407
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'G/lWH8wHKzv3ki6RzLcPUG8JyOtX0cM2'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

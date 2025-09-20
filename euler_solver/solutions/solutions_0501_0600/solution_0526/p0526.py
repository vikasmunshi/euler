#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 526: Largest Prime Factors of Consecutive Numbers.

Problem Statement:
    Let f(n) be the largest prime factor of n.
    Let g(n) = f(n) + f(n + 1) + f(n + 2) + f(n + 3) + f(n + 4) + f(n + 5) + f(n + 6)
    + f(n + 7) + f(n + 8), the sum of the largest prime factor of each of nine
    consecutive numbers starting with n.
    Let h(n) be the maximum value of g(k) for 2 ≤ k ≤ n.

    You are given:
        f(100) = 5
        f(101) = 101
        g(100) = 409
        h(100) = 417
        h(10^9) = 4896292593

    Find h(10^16).

URL: https://projecteuler.net/problem=526
"""
from typing import Any

euler_problem: int = 526
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

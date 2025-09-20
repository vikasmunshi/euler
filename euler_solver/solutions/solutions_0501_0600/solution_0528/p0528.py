#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 528: Constrained Sums.

Problem Statement:
    Let S(n, k, b) represent the number of valid solutions to x_1 + x_2 + ... + x_k <= n,
    where 0 <= x_m <= b^m for all 1 <= m <= k.

    For example, S(14, 3, 2) = 135, S(200, 5, 3) = 12949440, and
    S(1000, 10, 5) mod 1000000007 = 624839075.

    Find (sum from k=10 to 15 of S(10^k, k, k)) mod 1000000007.

URL: https://projecteuler.net/problem=528
"""
from typing import Any

euler_problem: int = 528
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 211: Divisor Square Sum.

Problem Statement:
    For a positive integer n, let sigma_2(n) be the sum of the squares of its
    divisors. For example, sigma_2(10) = 1 + 4 + 25 + 100 = 130.

    Find the sum of all n, 0 < n < 64,000,000 such that sigma_2(n) is a
    perfect square.

URL: https://projecteuler.net/problem=211
"""
from typing import Any

euler_problem: int = 211
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 64000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 100000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

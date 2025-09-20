#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 171: Square Sum of the Digital Squares.

Problem Statement:
    For a positive integer n, let f(n) be the sum of the squares of the digits
    (in base 10) of n, e.g.
    f(3) = 3^2 = 9
    f(25) = 2^2 + 5^2 = 4 + 25 = 29
    f(442) = 4^2 + 4^2 + 2^2 = 16 + 16 + 4 = 36

    Find the last nine digits of the sum of all n, 0 < n < 10^20, such that
    f(n) is a perfect square.

URL: https://projecteuler.net/problem=171
"""
from typing import Any

euler_problem: int = 171
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

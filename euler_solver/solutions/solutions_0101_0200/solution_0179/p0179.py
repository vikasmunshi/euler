#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 179: Consecutive Positive Divisors.

Problem Statement:
    Find the number of integers 1 < n < 10^7, for which n and n + 1 have the
    same number of positive divisors. For example, 14 has the positive
    divisors 1, 2, 7, 14 while 15 has 1, 3, 5, 15.

URL: https://projecteuler.net/problem=179
"""
from typing import Any

euler_problem: int = 179
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
    '9AepOYjAyZhb8QJU/VBy+thQIyE='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

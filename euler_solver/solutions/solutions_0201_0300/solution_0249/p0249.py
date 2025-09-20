#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 249: Prime Subset Sums.

Problem Statement:
    Let S = {2, 3, 5, ..., 4999} be the set of prime numbers less than 5000.
    Find the number of subsets of S, the sum of whose elements is a prime
    number.
    Enter the rightmost 16 digits as your answer.

URL: https://projecteuler.net/problem=249
"""
from typing import Any

euler_problem: int = 249
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 30}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 5000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 10000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

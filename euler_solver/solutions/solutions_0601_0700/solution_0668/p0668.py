#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 668: Square Root Smooth Numbers.

Problem Statement:
    A positive integer is called square root smooth if all of its prime factors are
    strictly less than its square root.
    Including the number 1, there are 29 square root smooth numbers not exceeding 100.

    How many square root smooth numbers are there not exceeding 10000000000?

URL: https://projecteuler.net/problem=668
"""
from typing import Any

euler_problem: int = 668
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

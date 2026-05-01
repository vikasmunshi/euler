#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 168: Number Rotations.

Problem Statement:
    Consider the number 142857. We can right-rotate this number by moving the
    last digit (7) to the front of it, giving us 714285.
    It can be verified that 714285 = 5 * 142857.
    This demonstrates an unusual property of 142857: it is a divisor of its
    right-rotation.

    Find the last 5 digits of the sum of all integers n, 10 < n < 10^100,
    that have this property.

URL: https://projecteuler.net/problem=168
"""
from typing import Any

euler_problem: int = 168
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10 ** 3},
     'answer': None},
    {'category': 'main', 'input': {'max_limit': 10 ** 100},
     'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

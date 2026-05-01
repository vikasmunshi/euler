#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 272: Modular Cubes, Part 2.

Problem Statement:
    For a positive number n, define C(n) as the number of integers x for which
    1 < x < n and x^3 ≡ 1 mod n.
    When n = 91 there are 8 possible values for x: 9, 16, 22, 29, 53, 74, 79,
    81. Thus, C(91) = 8.
    Find the sum of the positive numbers n ≤ 10^11 for which C(n) = 242.

URL: https://projecteuler.net/problem=272
"""
from typing import Any

euler_problem: int = 272
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    '03x3OeBJG2DsfKUR'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

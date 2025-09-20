#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 320: Factorials Divisible by a Huge Integer.

Problem Statement:
    Let N(i) be the smallest integer n such that n! is divisible by (i!)^1234567890.
    Let S(u) = sum N(i) for 10 <= i <= u.
    S(1000) = 614538266565663.
    Find S(1000000) mod 10^18.

URL: https://projecteuler.net/problem=320
"""
from typing import Any

euler_problem: int = 320
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 2000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'j38dAZeTnsK7OArI7PXmNQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

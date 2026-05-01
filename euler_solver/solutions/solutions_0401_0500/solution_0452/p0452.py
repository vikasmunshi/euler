#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 452: Long Products.

Problem Statement:
    Define F(m,n) as the number of n-tuples of positive integers for which the
    product of the elements doesn't exceed m.

    F(10, 10) = 571.

    F(10^6, 10^6) mod 1234567891 = 252903833.

    Find F(10^9, 10^9) mod 1234567891.

URL: https://projecteuler.net/problem=452
"""
from typing import Any

euler_problem: int = 452
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'m': 10, 'n': 10}, 'answer': None},
    {'category': 'main', 'input': {'m': 1000000000, 'n': 1000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

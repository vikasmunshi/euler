#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 719: Number Splitting.

Problem Statement:
    We define an S-number to be a natural number, n, that is a perfect square and
    its square root can be obtained by splitting the decimal representation of n
    into 2 or more numbers then adding the numbers.

    For example, 81 is an S-number because sqrt(81) = 8 + 1.
    6724 is an S-number: sqrt(6724) = 6 + 72 + 4.
    8281 is an S-number: sqrt(8281) = 8 + 2 + 81 = 82 + 8 + 1.
    9801 is an S-number: sqrt(9801) = 98 + 0 + 1.

    Further we define T(N) to be the sum of all S numbers n ≤ N. You are given
    T(10^4) = 41333.

    Find T(10^12).

URL: https://projecteuler.net/problem=719
"""
from typing import Any

euler_problem: int = 719
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'XlQGIZ0uoZvOANT7+Cw5ppnZc6A='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

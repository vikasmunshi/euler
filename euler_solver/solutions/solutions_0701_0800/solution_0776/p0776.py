#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 776: Digit Sum Division.

Problem Statement:
    For a positive integer n, d(n) is defined to be the sum of the digits of n.
    For example, d(12345) = 15.

    Let F(N) = sum from n = 1 to N of n / d(n).

    You are given F(10) = 19, F(123) approximately 1.187764610390e3 and
    F(12345) approximately 4.855801996238e6.

    Find F(1234567890123456789). Write your answer in scientific notation rounded
    to twelve significant digits after the decimal point. Use a lowercase e to
    separate the mantissa and the exponent.

URL: https://projecteuler.net/problem=776
"""
from typing import Any

euler_problem: int = 776
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1234567890123456789}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 100000000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'xXwQtffwLf0Z++m5XZpIJ1uBULw='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

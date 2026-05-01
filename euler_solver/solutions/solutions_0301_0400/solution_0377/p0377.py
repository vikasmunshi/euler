#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 377: Sum of Digits - Experience #13.

Problem Statement:
    There are 16 positive integers that do not have a zero in their digits and
    that have a digital sum equal to 5, namely:
    5, 14, 23, 32, 41, 113, 122, 131, 212, 221, 311, 1112, 1121, 1211,
    2111 and 11111.
    Their sum is 17891.

    Let f(n) be the sum of all positive integers that do not have a zero in
    their digits and have a digital sum equal to n.

    Find sum_{i=1}^{17} f(13^i).
    Give the last 9 digits as your answer.

URL: https://projecteuler.net/problem=377
"""
from typing import Any

euler_problem: int = 377
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'base': 13, 'max_power': 1}, 'answer': None},
    {'category': 'main', 'input': {'base': 13, 'max_power': 17}, 'answer': None},
    {'category': 'extra', 'input': {'base': 13, 'max_power': 20}, 'answer': None},
]
encrypted: str = (
    '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'
    '1uAlfU8FxbI='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

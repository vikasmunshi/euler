#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 323: Bitwise-OR Operations on Random Integers.

Problem Statement:
    Let y_0, y_1, y_2, ... be a sequence of random unsigned 32-bit integers
    (i.e. 0 <= y_i < 2^32, every value equally likely).

    For the sequence x_i the following recursion is given:

        x_0 = 0
        x_i = x_{i-1} | y_{i-1}, for i > 0. (| is the bitwise-OR operator)

    It can be seen that eventually there will be an index N such that
    x_i = 2^32 - 1 (a bit-pattern of all ones) for all i >= N.

    Find the expected value of N.
    Give your answer rounded to 10 digits after the decimal point.

URL: https://projecteuler.net/problem=323
"""
from typing import Any

euler_problem: int = 323
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'bits': 3}, 'answer': None},
    {'category': 'main', 'input': {'bits': 32}, 'answer': None},
    {'category': 'extra', 'input': {'bits': 64}, 'answer': None},
]
encrypted: str = (
    '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'
    'XDSqmCa7b58pxbNGWYsgKA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

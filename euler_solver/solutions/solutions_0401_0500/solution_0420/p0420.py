#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 420: 2 x 2 Positive Integer Matrix.

Problem Statement:
    A positive integer matrix is a matrix whose elements are all positive integers.
    Some positive integer matrices can be expressed as a square of a positive integer
    matrix in two different ways. Here is an example:

        40 12
        48 40

    equals

        2  3
       12  2

    squared and also

        6  1
        4  6

    squared.

    We define F(N) as the number of the 2x2 positive integer matrices which have a
    trace (the sum of the elements on the main diagonal) less than N and which can
    be expressed as a square of a positive integer matrix in two different ways.
    We can verify that F(50) = 7 and F(1000) = 1019.

    Find F(10^7).

URL: https://projecteuler.net/problem=420
"""
from typing import Any

euler_problem: int = 420
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_trace': 50}, 'answer': None},
    {'category': 'main', 'input': {'max_trace': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
    '3mnP42Kmmk65LJRE'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

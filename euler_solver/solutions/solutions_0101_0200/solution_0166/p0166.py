#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 166: Criss Cross.

Problem Statement:
    A 4 x 4 grid is filled with digits d, 0 <= d <= 9.

    It can be seen that in the grid
    6 3 3 0
    5 0 4 3
    0 7 1 4
    1 2 4 5
    the sum of each row and each column has the value 12. Moreover the sum
    of each diagonal is also 12.

    In how many ways can you fill a 4 x 4 grid with the digits d, 0 <= d <= 9
    so that each row, each column, and both diagonals have the same sum?

URL: https://projecteuler.net/problem=166
"""
from typing import Any

euler_problem: int = 166
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_digit': 1}, 'answer': None},
    {'category': 'main', 'input': {'max_digit': 9}, 'answer': None},
]
encrypted: str = (
    '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'
    'ADVnPyOMSJcibe5Y7Q5mpA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

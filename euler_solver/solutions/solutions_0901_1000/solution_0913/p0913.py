#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 913: Row-major vs Column-major.

Problem Statement:
    The numbers from 1 to 12 can be arranged into a 3 by 4 matrix in either row-major
    or column-major order:
        R = [[1, 2, 3, 4],
             [5, 6, 7, 8],
             [9, 10, 11, 12]]
        C = [[1, 4, 7, 10],
             [2, 5, 8, 11],
             [3, 6, 9, 12]]
    By swapping two entries at a time, at least 8 swaps are needed to transform R to C.

    Let S(n, m) be the minimal number of swaps needed to transform an n by m matrix of numbers
    1 to n*m from row-major order to column-major order. Thus S(3, 4) = 8.

    It is given that the sum of S(n, m) for 2 ≤ n ≤ m ≤ 100 is 12578833.

    Find the sum of S(n^4, m^4) for 2 ≤ n ≤ m ≤ 100.

URL: https://projecteuler.net/problem=913
"""
from typing import Any

euler_problem: int = 913
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

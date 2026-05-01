#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 559: Permuted Matrices.

Problem Statement:
    An ascent of a column j in a matrix occurs if the value of column j is smaller
    than the value of column j + 1 in all rows.

    Let P(k, r, n) be the number of r by n matrices with the following properties:
        - The rows are permutations of {1, 2, 3, ..., n}.
        - Numbering the first column as 1, a column ascent occurs at column j < n
          if and only if j is not a multiple of k.

    For example, P(1, 2, 3) = 19, P(2, 4, 6) = 65508751 and P(7, 5, 30) mod 1000000123 = 161858102.

    Let Q(n) = sum_{k=1}^n P(k, n, n). For example, Q(5) = 21879393751 and
    Q(50) mod 1000000123 = 819573537.

    Find Q(50000) mod 1000000123.

URL: https://projecteuler.net/problem=559
"""
from typing import Any

euler_problem: int = 559
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 5}, 'answer': None},
    {'category': 'main', 'input': {'n': 50000}, 'answer': None},
    {'category': 'extra', 'input': {'n': 100000}, 'answer': None},
]
encrypted: str = (
    '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'
    'zbQ9dw=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 782: Distinct Rows and Columns.

Problem Statement:
    The complexity of an n×n binary matrix is the number of distinct rows and columns.

    For example, consider the 3×3 matrices
        A = [[1,0,1],
             [0,0,0],
             [1,0,1]]
        B = [[0,0,0],
             [0,0,0],
             [1,1,1]]
    A has complexity 2 because the set of rows and columns is {000, 101}.
    B has complexity 3 because the set of rows and columns is {000, 001, 111}.

    For 0 <= k <= n^2, let c(n, k) be the minimum complexity of an n×n binary
    matrix with exactly k ones.

    Let
        C(n) = sum_{k=0}^{n^2} c(n, k)

    For example, C(2) = c(2, 0) + c(2, 1) + c(2, 2) + c(2, 3) + c(2, 4) = 1 + 2 + 2 + 2 + 1 = 8.
    Given: C(5) = 64, C(10) = 274, and C(20) = 1150.

    Find C(10^4).

URL: https://projecteuler.net/problem=782
"""
from typing import Any

euler_problem: int = 782
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

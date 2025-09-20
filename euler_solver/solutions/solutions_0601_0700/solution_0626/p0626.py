#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 626: Counting Binary Matrices.

Problem Statement:
    A binary matrix is a matrix consisting entirely of 0s and 1s. Consider the following
    transformations that can be performed on a binary matrix:

        - Swap any two rows
        - Swap any two columns
        - Flip all elements in a single row (1s become 0s, 0s become 1s)
        - Flip all elements in a single column

    Two binary matrices A and B will be considered equivalent if there is a sequence of such
    transformations that when applied to A yields B. For example, the following two matrices
    are equivalent:

    A = [[1, 0, 1],
         [0, 0, 1],
         [0, 0, 0]]

    B = [[0, 0, 0],
         [1, 0, 0],
         [0, 0, 1]]

    via the sequence of two transformations "Flip all elements in column 3" followed by
    "Swap rows 1 and 2".

    Define c(n) to be the maximum number of n×n binary matrices that can be found such that
    no two are equivalent. For example, c(3)=3. You are also given that c(5)=39 and c(8)=656108.

    Find c(20), and give your answer modulo 1001001011.

URL: https://projecteuler.net/problem=626
"""
from typing import Any

euler_problem: int = 626
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 20}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

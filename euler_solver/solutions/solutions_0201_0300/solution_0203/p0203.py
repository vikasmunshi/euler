#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 203: Squarefree Binomial Coefficients.

Problem Statement:
    The binomial coefficients C(n, k) can be arranged in triangular form,
    Pascal's triangle.

    It can be seen that the first eight rows of Pascal's triangle contain
    twelve distinct numbers: 1, 2, 3, 4, 5, 6, 7, 10, 15, 20, 21 and 35.

    A positive integer n is called squarefree if no square of a prime divides n.
    Of the twelve distinct numbers in the first eight rows of Pascal's
    triangle, all except 4 and 20 are squarefree. The sum of the distinct
    squarefree numbers in the first eight rows is 105.

    Find the sum of the distinct squarefree numbers in the first 51 rows of
    Pascal's triangle.

URL: https://projecteuler.net/problem=203
"""
from typing import Any

euler_problem: int = 203
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'rows': 8}, 'answer': None},
    {'category': 'main', 'input': {'rows': 51}, 'answer': None},
    {'category': 'extra', 'input': {'rows': 100}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

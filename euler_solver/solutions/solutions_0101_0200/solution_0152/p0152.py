#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 152: Sums of Square Reciprocals.

Problem Statement:
    There are several ways to write the number 1/2 as a sum of square
    reciprocals using distinct integers.

    For instance, the numbers {2, 3, 4, 5, 7, 12, 15, 20, 28, 35} can be used:

    1/2 = 1/2^2 + 1/3^2 + 1/4^2 + 1/5^2 +
         1/7^2 + 1/12^2 + 1/15^2 + 1/20^2 +
         1/28^2 + 1/35^2

    In fact, only using integers between 2 and 45 inclusive, there are exactly
    three ways to do it, the remaining two being:
    {2, 3, 4, 6, 7, 9, 10, 20, 28, 35, 36, 45} and
    {2, 3, 4, 6, 7, 9, 12, 15, 28, 30, 35, 36, 45}.

    How many ways are there to write 1/2 as a sum of reciprocals of squares
    using distinct integers between 2 and 80 inclusive?

URL: https://projecteuler.net/problem=152
"""
from typing import Any

euler_problem: int = 152
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 45}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 80}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 100}, 'answer': None},
]
encrypted: str = (
    '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'
    '+uM+pZLcDAan0O+cIutrBQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

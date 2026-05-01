#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 140: Modified Fibonacci Golden Nuggets.

Problem Statement:
    Consider the infinite polynomial series A_G(x) = x G_1 + x^2 G_2 + x^3 G_3
    + ..., where G_k is the k-th term of the second order recurrence
    G_k = G_{k-1} + G_{k-2}, G_1 = 1 and G_2 = 4; that is, 1, 4, 5, 9, 14, 23, ...
    For this problem we shall be concerned with values of x for which A_G(x)
    is a positive integer.

    The corresponding values of x for the first five natural numbers are:
    (sqrt(5)-1)/4 -> 1
    2/5             -> 2
    (sqrt(22)-2)/6  -> 3
    (sqrt(137)-5)/14-> 4
    1/2             -> 5

    We shall call A_G(x) a golden nugget if x is rational. For example, the
    20th golden nugget is 211345365.

    Find the sum of the first thirty golden nuggets.

URL: https://projecteuler.net/problem=140
"""
from typing import Any

euler_problem: int = 140
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 5}, 'answer': None},
    {'category': 'main', 'input': {'n': 30}, 'answer': None},
    {'category': 'extra', 'input': {'n': 50}, 'answer': None},
]
encrypted: str = (
    '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'
    'dbwUMN6Y1zKTAa2wt0jMuFoA+jU='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 137: Fibonacci Golden Nuggets.

Problem Statement:
    Consider the infinite polynomial series A_F(x) = x F1 + x^2 F2 + x^3 F3 + ...,
    where F_k is the k-th term in the Fibonacci sequence: 1, 1, 2, 3, 5, 8, ...
    that is, F_k = F_{k-1} + F_{k-2}, F1 = 1 and F2 = 1.

    For this problem we shall be interested in values of x for which A_F(x)
    is a positive integer.

    For example:
        A_F(1/2) = (1/2)*1 + (1/2)^2*1 + (1/2)^3*2 + (1/2)^4*3 + (1/2)^5*5 + ...
                 = 1/2 + 1/4 + 2/8 + 3/16 + 5/32 + ...
                 = 2

    The corresponding values of x for the first five natural numbers are:
        x = sqrt(2)-1           => A_F(x) = 1
        x = 1/2                 => A_F(x) = 2
        x = (sqrt(13)-2)/3      => A_F(x) = 3
        x = (sqrt(89)-5)/8      => A_F(x) = 4
        x = (sqrt(34)-3)/5      => A_F(x) = 5

    We shall call A_F(x) a golden nugget if x is rational, because they become
    increasingly rarer; for example, the 10th golden nugget is 74049690.

    Find the 15th golden nugget.

URL: https://projecteuler.net/problem=137
"""
from typing import Any

euler_problem: int = 137
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 5}, 'answer': None},
    {'category': 'main', 'input': {'n': 15}, 'answer': None},
    {'category': 'extra', 'input': {'n': 20}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

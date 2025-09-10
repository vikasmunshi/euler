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

Solution Approach:
    Use the Fibonacci generating function: A_F(x) = sum_{k>=1} F_k x^k = x/(1 - x - x^2).
    Set x/(1-x-x^2) = n and rearrange to get the quadratic n x^2 + (n+1) x - n = 0.
    Rational x requires the discriminant D = (n+1)^2 + 4 n^2 = 5 n^2 + 2 n + 1 to be a
    perfect square. This leads to a Pell-type Diophantine equation.
    Solve that Pell-type equation or use the resulting linear recurrence on n to
    generate the sequence of golden nuggets. Expect O(k) time to produce the k-th
    nugget and O(1) space beyond storing current recurrence terms.

Answer: ...
URL: https://projecteuler.net/problem=137
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 137
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 5}},
    {'category': 'main', 'input': {'n': 15}},
    {'category': 'extra', 'input': {'n': 20}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_fibonacci_golden_nuggets_p0137_s0(*, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
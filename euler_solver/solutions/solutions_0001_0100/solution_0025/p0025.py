#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 25: 1000-digit Fibonacci Number.

Problem Statement:
    The Fibonacci sequence is defined by the recurrence relation:
        F_n = F_{n - 1} + F_{n - 2}, where F_1 = 1 and F_2 = 1.
    Hence the first 12 terms will be:
        F_1 = 1
        F_2 = 1
        F_3 = 2
        F_4 = 3
        F_5 = 5
        F_6 = 8
        F_7 = 13
        F_8 = 21
        F_9 = 34
        F_10 = 55
        F_11 = 89
        F_12 = 144
    The 12th term, F_12, is the first term to contain three digits.

    What is the index of the first term in the Fibonacci sequence to contain 1000 digits?

Solution Approach:
    Use arithmetic to generate Fibonacci numbers iteratively until the number of digits
    reaches the target (1000). This involves simple iteration and digit length checks.
    Time complexity is O(N) where N is the index of the first term with 1000 digits.
    The approach is efficient as Python handles arbitrary precision integers.

Answer: 4782
URL: https://projecteuler.net/problem=25
"""
from __future__ import annotations

from typing import Any

from euler_solver.framework import evaluate, logger, register_solution

euler_problem: int = 25
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3}, 'answer': 12},
    {'category': 'main', 'input': {'n': 1000}, 'answer': 4782},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve__1000_digit_fibonacci_number_p0025_s0(*, n: int) -> int:
    a, b = (1, 1)
    i = 2
    while b < 10 ** (n - 1):
        a, b = (b, a + b)
        i += 1
    return i


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

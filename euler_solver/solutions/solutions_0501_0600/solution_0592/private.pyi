#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 592: Factorial Trailing Digits 2.

Problem Statement:
    For any N, let f(N) be the last twelve hexadecimal digits before the trailing
    zeroes in N!.

    For example, the hexadecimal representation of 20! is 21C3677C82B40000,
    so f(20) is the digit sequence 21C3677C82B4.

    Find f(20!). Give your answer as twelve hexadecimal digits, using uppercase
    for the digits A to F.

Solution Approach:
    Use number theory and modular arithmetic to isolate the last twelve nonzero
    hexadecimal digits of factorial numbers. Carefully remove factors of 2 and 5
    (which cause trailing zeros) from the factorial. Efficient modular exponentiation
    and prime factorization techniques will help. Expected complexity depends on
    optimized arithmetic for large factorials.

Answer: ...
URL: https://projecteuler.net/problem=592
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 592
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_factorial_trailing_digits_2_p0592_s0() -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
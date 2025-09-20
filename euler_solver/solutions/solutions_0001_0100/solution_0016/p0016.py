#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 16: Power Digit Sum.

Problem Statement:
    2^15 = 32768 and the sum of its digits is 3 + 2 + 7 + 6 + 8 = 26.

    What is the sum of the digits of the number 2^1000?

Solution Approach:
    Use fast exponentiation to compute 2^1000 efficiently as a large integer.
    Convert the number to a string and sum its digits.
    The problem involves basic big integer arithmetic and string manipulation.
    Time complexity is dominated by exponentiation, effectively O(log n).

Answer: 1366
URL: https://projecteuler.net/problem=16
"""
from __future__ import annotations

from typing import Any

from euler_solver.framework import evaluate, logger, register_solution

euler_problem: int = 16
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'base': 2, 'power': 15}, 'answer': 26},
    {'category': 'main', 'input': {'base': 2, 'power': 1000}, 'answer': 1366},
    {'category': 'extra', 'input': {'base': 2, 'power': 10000}, 'answer': 13561},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_power_digit_sum_p0016_s0(*, base: int, power: int) -> int:
    return sum((int(i) for i in str(base ** power)))


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

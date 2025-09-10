#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 377: Sum of Digits - Experience #13.

Problem Statement:
    There are 16 positive integers that do not have a zero in their digits and
    that have a digital sum equal to 5, namely:
    5, 14, 23, 32, 41, 113, 122, 131, 212, 221, 311, 1112, 1121, 1211,
    2111 and 11111.
    Their sum is 17891.

    Let f(n) be the sum of all positive integers that do not have a zero in
    their digits and have a digital sum equal to n.

    Find sum_{i=1}^{17} f(13^i).
    Give the last 9 digits as your answer.

Solution Approach:
    Model valid integers as sequences of digits drawn from 1..9 whose parts sum
    to n. Use generating functions or digit dynamic programming to compute both
    the count of such sequences and the total numeric sum contributed by each
    digit position. Extract coefficients for compositions with parts 1..9 and
    aggregate place-value contributions to form f(n).
    For large exponents (13^i) use exponentiation techniques on power series or
    fast convolution (FFT) and perform all arithmetic modulo 10^9 to obtain the
    last 9 digits. Expected complexity depends on the convolution method:
    naive DP O(n*9) per n, FFT-based methods are faster for very large n.

Answer: ...
URL: https://projecteuler.net/problem=377
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 377
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'base': 13, 'max_power': 1}},
    {'category': 'main', 'input': {'base': 13, 'max_power': 17}},
    {'category': 'extra', 'input': {'base': 13, 'max_power': 20}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_sum_of_digits_experience_13_p0377_s0(*, base: int, max_power: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
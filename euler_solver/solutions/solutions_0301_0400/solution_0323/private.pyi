#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 323: Bitwise-OR Operations on Random Integers.

Problem Statement:
    Let y_0, y_1, y_2, ... be a sequence of random unsigned 32-bit integers
    (i.e. 0 <= y_i < 2^32, every value equally likely).

    For the sequence x_i the following recursion is given:

        x_0 = 0
        x_i = x_{i-1} | y_{i-1}, for i > 0. (| is the bitwise-OR operator)

    It can be seen that eventually there will be an index N such that
    x_i = 2^32 - 1 (a bit-pattern of all ones) for all i >= N.

    Find the expected value of N.
    Give your answer rounded to 10 digits after the decimal point.

Solution Approach:
    Model each bit position independently: for a given bit the time until it
    first becomes 1 is geometric with p = 1/2. Hence N is the maximum of 32
    iid geometric(1/2) variables. Use tail-sum formula:
        E[N] = sum_{t>=0} P(max > t) = sum_{t>=0} 1 - (1 - 2^{-t})^{32}.
    Compute this sum numerically to required precision, or expand using the
    binomial theorem and sum the resulting geometric series for a closed form.
    Use high-precision arithmetic; complexity is roughly O(bits * terms).
    Space complexity O(1).

Answer: ...
URL: https://projecteuler.net/problem=323
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 323
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'bits': 3}},
    {'category': 'main', 'input': {'bits': 32}},
    {'category': 'extra', 'input': {'bits': 64}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_bitwise_or_operations_on_random_integers_p0323_s0(*, bits: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
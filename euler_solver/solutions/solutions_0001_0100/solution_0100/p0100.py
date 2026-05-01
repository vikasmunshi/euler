#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 100: Arranged Probability.

Problem Statement:
    If a box contains twenty-one coloured discs, composed of fifteen blue discs and six
    red discs, and two discs were taken at random, it can be seen that the probability
    of taking two blue discs, P(BB) = (15/21) * (14/20) = 1/2.

    The next such arrangement, for which there is exactly 50% chance of taking two blue
    discs at random, is a box containing eighty-five blue discs and thirty-five red discs.

    By finding the first arrangement to contain over 10^12 = 1,000,000,000,000 discs in
    total, determine the number of blue discs that the box would contain.

Solution Approach:
    Model the problem as a Pell's equation derived from the probability condition.
    Use number theory to find the integer solutions efficiently, exploiting recurrence
    relations for successive solutions. The approach runs in O(log n) time relative to
    the number size, thanks to the rapid growth of solution terms.

Answer: 756872327473
URL: https://projecteuler.net/problem=100
"""
from __future__ import annotations

from typing import Any

from euler_solver.framework import evaluate, logger, register_solution

euler_problem: int = 100
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'total_discs': 21}, 'answer': 15},
    {'category': 'dev', 'input': {'total_discs': 120}, 'answer': 85},
    {'category': 'main', 'input': {'total_discs': 1000000000000}, 'answer': 756872327473},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_arranged_probability_p0100_s0(*, total_discs: int) -> int:
    x, y = (1, 1)
    while True:
        x, y = (3 * x + 4 * y, 2 * x + 3 * y)
        n = (x + 1) // 2
        b = (y + 1) // 2
        if n >= total_discs:
            return b


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 52: Permuted Multiples.

Problem Statement:
    It can be seen that the number, 125874, and its double, 251748, contain exactly the
    same digits, but in a different order.

    Find the smallest positive integer, x, such that 2x, 3x, 4x, 5x, and 6x, contain the
    same digits.

Solution Approach:
    Use digit frequency comparison to check permutations for multiples 2x to 6x.
    Iterate over integers and test the condition by sorting digits or using count arrays.
    Efficient checks and early termination reduce complexity.

Answer: 142857
URL: https://projecteuler.net/problem=52
"""
from __future__ import annotations

import sys
from typing import Any

from euler_solver.framework import evaluate, logger, register_solution

euler_problem: int = 52
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'multiples': 2}, 'answer': 125874},
    {'category': 'dev', 'input': {'multiples': 3}, 'answer': 142857},
    {'category': 'dev', 'input': {'multiples': 4}, 'answer': 142857},
    {'category': 'dev', 'input': {'multiples': 5}, 'answer': 142857},
    {'category': 'main', 'input': {'multiples': 6}, 'answer': 142857},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_permuted_multiples_p0052_s0(*, multiples: int) -> int:
    if not (isinstance(multiples, int) and 1 < multiples < 7):
        raise ValueError('multiples must be an integer between 2 and 6, both inclusive.')
    multiples_range = tuple(range(1, multiples + 1))
    for i in range(1, sys.maxsize // multiples):
        if len({''.join(sorted(str(i * multiple))) for multiple in multiples_range}) == 1:
            return i
    else:
        raise ValueError('No solution found')


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 9: Special Pythagorean Triplet.

Problem Statement:
    A Pythagorean triplet is a set of three natural numbers, a < b < c, for which,
    a^2 + b^2 = c^2.

    For example, 3^2 + 4^2 = 9 + 16 = 25 = 5^2.

    There exists exactly one Pythagorean triplet for which a + b + c = 1000.
    Find the product abc.

Solution Approach:
    Use number theory and algebraic manipulation to reduce the search space.
    Iterate efficiently over pairs (a, b) to find c = 1000 - a - b and check the
    Pythagorean condition. Time complexity O(n^2) is feasible for n=1000.

Answer: 31875000
URL: https://projecteuler.net/problem=9
"""
from __future__ import annotations

from typing import Any

from euler_solver.framework import evaluate, logger, register_solution

euler_problem: int = 9
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'sum_sides': 12}, 'answer': 60},
    {'category': 'main', 'input': {'sum_sides': 1000}, 'answer': 31875000},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_special_pythagorean_triplet_p0009_s0(*, sum_sides: int) -> int:
    try:
        return next((a * b * c for a in range(1, sum_sides // 4 + 1) for b in range(a, sum_sides // 2) for c in
                     (sum_sides - a - b,) if a ** 2 + b ** 2 == c ** 2))
    except StopIteration:
        raise ValueError(f'No Pythagorean triplet exists with sum {sum_sides}')


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

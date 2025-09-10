#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 398: Cutting Rope.

Problem Statement:
    Inside a rope of length n, n - 1 points are placed with distance 1 from
    each other and from the endpoints. Among these points, we choose m - 1
    points at random and cut the rope at these points to create m segments.

    Let E(n, m) be the expected length of the second-shortest segment.
    For example, E(3, 2) = 2 and E(8, 3) = 16/7. Note that if multiple
    segments have the same shortest length the length of the second-shortest
    segment is defined as the same as the shortest length.

    Find E(10^7, 100). Give your answer rounded to 5 decimal places behind
    the decimal point.

Solution Approach:
    Model the m segment lengths as a random composition of n into m positive
    integer parts (uniform over choices of m-1 cut points among n-1).
    Use combinatorics/order-statistics for discrete spacings to derive the
    distribution of the k-th smallest segment. Compute E(second-smallest)
    by summing tail probabilities or using closed-form combinatorial sums.
    Key ideas: combinatorics of compositions, cumulative distribution sums,
    efficient evaluation of binomial sums and prefix sums. Aim for O(m * polylog n).

Answer: ...
URL: https://projecteuler.net/problem=398
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 398
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3, 'm': 2}},
    {'category': 'main', 'input': {'n': 10000000, 'm': 100}},
    {'category': 'extra', 'input': {'n': 100000, 'm': 100}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_cutting_rope_p0398_s0(*, n: int, m: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
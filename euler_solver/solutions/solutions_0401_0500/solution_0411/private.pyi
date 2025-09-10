#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 411: Uphill Paths.

Problem Statement:
    Let n be a positive integer. Suppose there are stations at the coordinates
    (x, y) = (2^i mod n, 3^i mod n) for 0 <= i <= 2n. We consider stations with
    the same coordinates as the same station.

    We wish to form a path from (0, 0) to (n, n) such that the x and y coordinates
    never decrease.
    Let S(n) be the maximum number of stations such a path can pass through.

    For example, if n = 22, there are 11 distinct stations, and a valid path can
    pass through at most 5 stations. Therefore, S(22) = 5.
    The case is illustrated with an example of an optimal path.

    It can also be verified that S(123) = 14 and S(10000) = 48.

    Find the sum of S(k^5) for 1 <= k <= 30.

Solution Approach:
    Use modular arithmetic to generate station coordinates from powers of 2 and 3 mod n.
    Compute distinct stations up to 2n iterations, then find the longest non-decreasing
    path from (0,0) to (n,n) through these stations.
    Approach involves coordinate compression, sorting, and using Longest Increasing Subsequence
    (LIS) variants or dynamic programming with efficient data structures.
    Time complexity depends on n but should be optimized with careful pruning.

Answer: ...
URL: https://projecteuler.net/problem=411
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 411
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 22}},
    {'category': 'main', 'input': {'max_limit': 6436343}},  # 30^5 = 24300000, adjusted to a smaller for test;
]

@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_uphill_paths_p0411_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
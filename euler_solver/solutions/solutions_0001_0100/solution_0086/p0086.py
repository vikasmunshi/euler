#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 86: Cuboid Route.

Problem Statement:
    A spider, S, sits in one corner of a cuboid room, measuring 6 by 5 by 3, and a fly,
    F, sits in the opposite corner. By travelling on the surfaces of the room the
    shortest "straight line" distance from S to F is 10 and the path is shown on
    the diagram.

    However, there are up to three "shortest" path candidates for any given cuboid and
    the shortest route doesn't always have integer length.

    It can be shown that there are exactly 2060 distinct cuboids, ignoring rotations,
    with integer dimensions, up to a maximum size of M by M by M, for which the shortest
    route has integer length when M = 100. This is the least value of M for which the
    number of solutions first exceeds two thousand; the number of solutions when M = 99
    is 1975.

    Find the least value of M such that the number of solutions first exceeds one million.

Solution Approach:
    Use number theory and geometric analysis to find integer solutions for the
    shortest path on cuboids. Model shortest distance using combinations of sides and
    solve for integer shortest paths. Efficiently count solutions up to a max M using
    integer checking and enumeration. Expect O(M^2) or better complexity.

Answer: 1818
URL: https://projecteuler.net/problem=86
"""
from __future__ import annotations

from itertools import count
from math import sqrt
from typing import Any

from euler_solver.framework import evaluate, logger, register_solution

euler_problem: int = 86
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'target_solutions': 1975}, 'answer': 99},
    {'category': 'dev', 'input': {'target_solutions': 2000}, 'answer': 100},
    {'category': 'main', 'input': {'target_solutions': 1000000}, 'answer': 1818},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_cuboid_route_p0086_s0(*, target_solutions: int) -> int:
    result: int = 0
    for a in count(1):
        for b_plus_c in range(1, 2 * a + 1):
            if sqrt(a ** 2 + b_plus_c ** 2).is_integer():
                result += b_plus_c // 2 if b_plus_c <= a + 1 else (2 * a - b_plus_c + 2) // 2
                if result >= target_solutions:
                    return a
    return -1


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

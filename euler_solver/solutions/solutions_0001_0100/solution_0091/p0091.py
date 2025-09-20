#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 91: Right Triangles with Integer Coordinates.

Problem Statement:
    The points P(x1, y1) and Q(x2, y2) are plotted at integer coordinates and
    are joined to the origin, O(0,0), to form triangle OPQ.

    There are exactly fourteen triangles containing a right angle that can be
    formed when each coordinate lies between 0 and 2 inclusive; that is,
    0 <= x1, y1, x2, y2 <= 2.

    Given that 0 <= x1, y1, x2, y2 <= 50, how many right triangles can be
    formed?

Solution Approach:
    Use coordinate geometry and vector dot product to test for right angles.
    Enumerate all points in the grid and count triples (O, P, Q) with the right
    angle at any vertex using properties of dot products.
    Implementation should be efficient with O(N^2) complexity for N=50.

Answer: 14234
URL: https://projecteuler.net/problem=91
"""
from __future__ import annotations

from math import gcd
from typing import Any

from euler_solver.framework import evaluate, logger, register_solution

euler_problem: int = 91
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'coordinate_limit': 2}, 'answer': 14},
    {'category': 'main', 'input': {'coordinate_limit': 50}, 'answer': 14234},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_right_triangles_with_integer_coordinates_p0091_s0(*, coordinate_limit: int) -> int:
    triangles_at_p_or_q = sum((min(x * m // y, m * (coordinate_limit - y) // x)
                               for x in range(1, coordinate_limit + 1)
                               for y in range(1, coordinate_limit)
                               for m in [gcd(x, y)]))
    triangles_at_p_or_q *= 2
    triangles_at_origin = 3 * coordinate_limit ** 2
    return triangles_at_p_or_q + triangles_at_origin


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

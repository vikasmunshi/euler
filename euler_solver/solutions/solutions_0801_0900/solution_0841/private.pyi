#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 841: Regular Star Polygons.

Problem Statement:
    The regular star polygon {p/q}, for coprime integers p,q with p > 2q > 0, is a polygon
    formed from p edges of equal length and equal internal angles, such that tracing the
    complete polygon wraps q times around the centre. For example, {8/3} is illustrated.

    The edges of a regular star polygon intersect one another, dividing the interior into
    several regions. Define the alternating shading of a regular star polygon to be a
    selection of such regions to shade, such that every piece of every edge has a shaded
    region on one side and an unshaded region on the other, with the exterior of the polygon
    unshaded. The example shows the alternating shading (in green) of {8/3}.

    Let A(p, q) be the area of the alternating shading of {p/q}, assuming its inradius is 1.
    (The inradius of a regular polygon, star or otherwise, is the distance from its centre to
    the midpoint of any of its edges.) For the example, it can be shown that the central
    shaded octagon has area 8(√2 - 1) and each point's shaded kite has area 2(√2 - 1), giving
    A(8,3) = 24(√2 - 1) approximately 9.9411254970.

    You are also given that A(130021, 50008) ≈ 10.9210371479, rounded to 10 digits after
    the decimal point.

    Find the sum from n=3 to 34 of A(F_{n+1}, F_{n-1}), where F_j is the Fibonacci sequence
    with F_1=F_2=1 (so A(F_6,F_4) = A(8,3)).
    Give your answer rounded to 10 digits after the decimal point.

Solution Approach:
    Use geometry and number theory to understand the structure of regular star polygons.
    Employ properties of the Fibonacci sequence in parametrizing p and q. Calculate areas
    using polygon inradius and trigonometric relations, summing the alternating shading
    areas A(F_{n+1},F_{n-1}). Numeric methods or closed-form formulas may be used for the
    area with arbitrary precision. The approach involves geometry, trigonometry, and recurrence
    sequences with O(n) complexity.

Answer: ...
URL: https://projecteuler.net/problem=841
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 841
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_regular_star_polygons_p0841_s0() -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
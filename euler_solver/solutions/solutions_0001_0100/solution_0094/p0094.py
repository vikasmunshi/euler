#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 94: Almost Equilateral Triangles.

Problem Statement:
    It is easily proved that no equilateral triangle exists with integral length
    sides and integral area. However, the almost equilateral triangle 5-5-6 has
    an area of 12 square units.

    We shall define an almost equilateral triangle to be a triangle for which two
    sides are equal and the third differs by no more than one unit.

    Find the sum of the perimeters of all almost equilateral triangles with
    integral side lengths and area and whose perimeters do not exceed one billion
    (1000000000).

Solution Approach:
    Use number theory and Diophantine equations to characterize almost equilateral
    triangles with integral area. Exploit the relation between side lengths and
    area via Heron's formula, leading to Pell-type equations. Enumerate solutions
    efficiently while checking perimeter constraints. Expected complexity dominated
    by number of solutions under 1e9 perimeter.

Answer: 518408346
URL: https://projecteuler.net/problem=94
"""
from __future__ import annotations

from typing import Any

from euler_solver.framework import evaluate, logger, register_solution

euler_problem: int = 94
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'max_perimeter': 1000000000}, 'answer': 518408346},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_almost_equilateral_triangles_p0094_s0(*, max_perimeter: int) -> int:
    s, s1, s2, m, p = (0, 1, 1, 1, 0)
    while p <= max_perimeter:
        s, s1, s2, m = (s + p, s2, 4 * s2 - s1 + 2 * m, -m)
        p = 3 * s2 - m
    return s


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

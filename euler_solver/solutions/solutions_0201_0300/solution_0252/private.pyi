#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 252: Convex Holes.

Problem Statement:
    Given a set of points on a plane, we define a convex hole to be a convex
    polygon having as vertices any of the given points and not containing any
    of the given points in its interior (points may lie on the perimeter).

    For example, the image in the problem statement shows twenty points and a
    few convex holes. The red heptagon shown has area 1049694.5, which is the
    maximum area convex hole for that example set.

    For the example we used the first 20 points (T_{2k-1}, T_{2k}), for
    k = 1,2,...,20, produced with the pseudo-random generator:
        S_0 = 290797
        S_{n+1} = S_n^2 mod 50515093
        T_n = (S_n mod 2000) - 1000
    i.e. (527, 144), (-488, 732), (-454, -947), ...

    What is the maximum area for a convex hole on the set containing the
    first 500 points in the pseudo-random sequence? Specify your answer
    including one digit after the decimal point.

Solution Approach:
    Generate the first n points from the given linear congruential-like PRNG.
    Interpret the problem as finding the largest-area empty convex polygon
    whose vertices are a subset of the points (interior contains no points).
    Key ideas: computational geometry, convexity tests, area via triangle sums,
    and dynamic programming over directed edges or polygon chains to combine
    empty triangles into larger empty convex polygons.
    Precompute emptiness/area of all triangles (O(n^3) checks overall) and
    use DP to extend chains while preserving convexity and emptiness.
    Expected complexity: roughly O(n^3) time and O(n^2) memory; optimize point
    in-triangle tests and use integer arithmetic where possible.

Answer: ...
URL: https://projecteuler.net/problem=252
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 252
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 20}},
    {'category': 'main', 'input': {'n': 500}},
    {'category': 'extra', 'input': {'n': 1000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_convex_holes_p0252_s0(*, n: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 465: Polar Polygons.

Problem Statement:
    The kernel of a polygon is defined by the set of points from which the entire
    polygon's boundary is visible. We define a polar polygon as a polygon for which
    the origin is strictly contained inside its kernel.

    For this problem, a polygon can have collinear consecutive vertices. However,
    a polygon still cannot have self-intersection and cannot have zero area.

    For example, only the first of several example polygons is a polar polygon
    (their kernels exclude the origin or do not exist for the others).

    Notice that the first polygon has three consecutive collinear vertices.

    Let P(n) be the number of polar polygons such that the vertices (x, y) have
    integer coordinates whose absolute values are not greater than n.

    Polygons are distinct if they have different sets of edges, even if they enclose
    the same area. For example, the polygon with vertices [(0,0),(0,3),(1,1),(3,0)]
    is distinct from the polygon with vertices [(0,0),(0,3),(1,1),(3,0),(1,0)].

    Examples: P(1) = 131, P(2) = 1648531, P(3) = 1099461296175, and
    P(343) mod 1,000,000,007 = 937293740.

    Find P(7^13) mod 1,000,000,007.

URL: https://projecteuler.net/problem=465
"""
from typing import Any

euler_problem: int = 465
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 62748517}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

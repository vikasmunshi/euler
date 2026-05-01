#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 742: Minimum Area of a Convex Grid Polygon.

Problem Statement:
    A symmetrical convex grid polygon is a polygon such that:
        - All its vertices have integer coordinates.
        - All its internal angles are strictly smaller than 180 degrees.
        - It has both horizontal and vertical symmetry.

    For example, the left polygon is a convex grid polygon which has neither horizontal
    nor vertical symmetry, while the right one is a valid symmetrical convex grid polygon
    with six vertices.

    Define A(N), the minimum area of a symmetrical convex grid polygon with N vertices.

    You are given A(4) = 1, A(8) = 7, A(40) = 1039 and A(100) = 17473.

    Find A(1000).

URL: https://projecteuler.net/problem=742
"""
from typing import Any

euler_problem: int = 742
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 1000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 564: Maximal Polygons.

Problem Statement:
    A line segment of length 2n-3 is randomly split into n segments of integer
    length (n ≥ 3). In the sequence given by this split, the segments are then
    used as consecutive sides of a convex n-polygon, formed in such a way that
    its area is maximal. All of the C(2n-4, n-1) possibilities for splitting up
    the initial line segment occur with the same probability.

    Let E(n) be the expected value of the area that is obtained by this procedure.
    For example, for n=3 the only possible split of the line segment of length 3
    results in three line segments with length 1, that form an equilateral
    triangle with an area of (1/4)*sqrt(3). Therefore E(3)=0.433013, rounded to 6
    decimal places.
    For n=4 you can find 4 different possible splits, each composed of three line
    segments with length 1 and one line segment with length 2. All of these splits
    lead to the same maximal quadrilateral with an area of (3/4)*sqrt(3), thus
    E(4)=1.299038, rounded to 6 decimal places.

    Let S(k)= sum_{n=3}^k E(n).
    For example, S(3)=0.433013, S(4)=1.732051, S(5)=4.604767 and S(10)=66.955511,
    rounded to 6 decimal places each.

    Find S(50), rounded to 6 decimal places.

URL: https://projecteuler.net/problem=564
"""
from typing import Any

euler_problem: int = 564
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'k': 50}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

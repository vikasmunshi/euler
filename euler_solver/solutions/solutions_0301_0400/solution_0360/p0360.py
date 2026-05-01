#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 360: Scary Sphere.

Problem Statement:
    Given two points (x1, y1, z1) and (x2, y2, z2) in three dimensional space,
    the Manhattan distance between those points is defined as
    |x1 - x2| + |y1 - y2| + |z1 - z2|.

    Let C(r) be a sphere with radius r and center in the origin O(0,0,0).
    Let I(r) be the set of all points with integer coordinates on the
    surface of C(r).
    Let S(r) be the sum of the Manhattan distances of all elements of I(r)
    to the origin O.

    E.g. S(45)=34518.

    Find S(10^10).

URL: https://projecteuler.net/problem=360
"""
from typing import Any

euler_problem: int = 360
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'r': 45}, 'answer': None},
    {'category': 'main', 'input': {'r': 10000000000}, 'answer': None},
    {'category': 'extra', 'input': {'r': 1000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

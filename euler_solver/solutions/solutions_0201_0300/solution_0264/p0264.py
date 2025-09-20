#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 264: Triangle Centres.

Problem Statement:
    Consider all the triangles having:
    All their vertices on lattice points (integer coordinates).
    Circumcentre at the origin O.
    Orthocentre at the point H(5, 0).

    There are nine such triangles having a perimeter <= 50. Listed and shown in
    ascending order of their perimeter, they are:
    A(-4, 3), B(5, 0), C(4, -3)
    A(4, 3), B(5, 0), C(-4, -3)
    A(-3, 4), B(5, 0), C(3, -4)
    A(3, 4), B(5, 0), C(-3, -4)
    A(0, 5), B(5, 0), C(0, -5)
    A(1, 8), B(8, -1), C(-4, -7)
    A(8, 1), B(1, -8), C(-4, 7)
    A(2, 9), B(9, -2), C(-6, -7)
    A(9, 2), B(2, -9), C(-6, 7)

    The sum of their perimeters, rounded to four decimal places, is 291.0089.

    Find all such triangles with a perimeter <= 10^5.
    Enter as your answer the sum of their perimeters rounded to four decimals.

URL: https://projecteuler.net/problem=264
"""
from typing import Any

euler_problem: int = 264
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 50}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

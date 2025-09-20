#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 295: Lenticular Holes.

Problem Statement:
    We call the convex area enclosed by two circles a lenticular hole if:
        - The centres of both circles are on lattice points.
        - The two circles intersect at two distinct lattice points.
        - The interior of the convex area enclosed by both circles does not
          contain any lattice points.

    Consider the circles:
        C0: x^2 + y^2 = 25
        C1: (x + 4)^2 + (y - 4)^2 = 1
        C2: (x - 12)^2 + (y - 4)^2 = 65

    C0 and C1 form a lenticular hole, as well as C0 and C2.

    We call an ordered pair of positive real numbers (r1, r2) a lenticular
    pair if there exist two circles with radii r1 and r2 that form a
    lenticular hole. For the example above (1, 5) and (5, sqrt(65)) are
    lenticular pairs.

    Let L(N) be the number of distinct lenticular pairs (r1, r2) for which
    0 < r1 <= r2 <= N. We can verify that L(10) = 30 and L(100) = 3442.

    Find L(100000).

URL: https://projecteuler.net/problem=295
"""
from typing import Any

euler_problem: int = 295
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 200000}, 'answer': None},
]
encrypted: str = (
    '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'
    'p8WisoyS0nSovcesp06Ie0KcLaQa15iapHlTjg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

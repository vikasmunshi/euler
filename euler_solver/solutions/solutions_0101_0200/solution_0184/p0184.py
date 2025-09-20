#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 184: Triangles Containing the Origin.

Problem Statement:
    Consider the set I_r of points (x,y) with integer co-ordinates in the
    interior of the circle with radius r, centered at the origin, i.e.
    x^2 + y^2 < r^2.

    For a radius of 2, I_2 contains the nine points (0,0), (1,0), (1,1),
    (0,1), (-1,1), (-1,0), (-1,-1), (0,-1) and (1,-1). There are eight
    triangles having all three vertices in I_2 which contain the origin in
    the interior.

    For a radius of 3, there are 360 triangles containing the origin with
    all vertices in I_3, and for I_5 the number is 10600.

    How many triangles are there containing the origin in the interior and
    having all three vertices in I_105?

URL: https://projecteuler.net/problem=184
"""
from typing import Any

euler_problem: int = 184
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'r': 2}, 'answer': None},
    {'category': 'main', 'input': {'r': 105}, 'answer': None},
]
encrypted: str = (
    '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'
    '/An9ie6oJPlIXIaqzb6/K5r/iUSsdZU3'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

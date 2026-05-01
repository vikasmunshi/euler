#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 894: Spiral of Circles.

Problem Statement:
    Consider a unit circle C0 on the plane that does not enclose the origin.
    For k≥1, a circle Ck is created by scaling and rotating C(k-1) with respect
    to the origin. Both the radius and the distance to the origin are scaled
    by the same factor, and the centre of rotation is the origin. The scaling
    factor is positive and strictly less than one. Both it and the rotation
    angle remain constant for each k.

    It is given that C0 is externally tangent to C1, C7 and C8, as shown in the
    diagram, and no two circles overlap.

    Find the total area of all the circular triangles in the diagram, i.e.
    the area painted green above.
    Give your answer rounded to 10 places after the decimal point.

URL: https://projecteuler.net/problem=894
"""
from typing import Any

euler_problem: int = 894
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

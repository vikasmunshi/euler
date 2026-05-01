#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 841: Regular Star Polygons.

Problem Statement:
    The regular star polygon {p/q}, for coprime integers p,q with p > 2q > 0, is a polygon
    formed from p edges of equal length and equal internal angles, such that tracing the
    complete polygon wraps q times around the centre. For example, {8/3} is illustrated.

    The edges of a regular star polygon intersect one another, dividing the interior into
    several regions. Define the alternating shading of a regular star polygon to be a
    selection of such regions to shade, such that every piece of every edge has a shaded
    region on one side and an unshaded region on the other, with the exterior of the polygon
    unshaded. The example shows the alternating shading (in green) of {8/3}.

    Let A(p, q) be the area of the alternating shading of {p/q}, assuming its inradius is 1.
    (The inradius of a regular polygon, star or otherwise, is the distance from its centre to
    the midpoint of any of its edges.) For the example, it can be shown that the central
    shaded octagon has area 8(√2 - 1) and each point's shaded kite has area 2(√2 - 1), giving
    A(8,3) = 24(√2 - 1) approximately 9.9411254970.

    You are also given that A(130021, 50008) ≈ 10.9210371479, rounded to 10 digits after
    the decimal point.

    Find the sum from n=3 to 34 of A(F_{n+1}, F_{n-1}), where F_j is the Fibonacci sequence
    with F_1=F_2=1 (so A(F_6,F_4) = A(8,3)).
    Give your answer rounded to 10 digits after the decimal point.

URL: https://projecteuler.net/problem=841
"""
from typing import Any

euler_problem: int = 841
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

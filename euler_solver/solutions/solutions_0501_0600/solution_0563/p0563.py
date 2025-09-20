#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 563: Robot Welders.

Problem Statement:
    A company specialises in producing large rectangular metal sheets, starting
    from unit square metal plates. The welding is performed by a range of robots
    of increasing size. Unfortunately, the programming options of these robots
    are rather limited. Each one can only process up to 25 identical rectangles
    of metal, which they can weld along either edge to produce a larger rectangle.
    The only programmable variables are the number of rectangles to be processed
    (up to and including 25), and whether to weld the long or short edge.

    For example, the first robot could be programmed to weld together 11 raw unit
    square plates to make a 11 x 1 strip. The next could take 10 of these 11 x 1
    strips, and weld them either to make a longer 110 x 1 strip, or a 11 x 10
    rectangle. Many, but not all, possible dimensions of metal sheets can be
    constructed in this way.

    One regular customer has a particularly unusual order: The finished product
    should have an exact area, and the long side must not be more than 10% larger
    than the short side. If these requirements can be met in more than one way,
    in terms of the exact dimensions of the two sides, then the customer will demand
    that all variants be produced. For example, if the order calls for a metal sheet
    of area 889200, then there are three final dimensions that can be produced:
    900 x 988, 912 x 975 and 936 x 950. The target area of 889200 is the smallest
    area which can be manufactured in three different variants, within the
    limitations of the robot welders.

    Let M(n) be the minimal area that can be manufactured in exactly n variants
    with the longer edge not greater than 10% bigger than the shorter edge.
    Hence M(3) = 889200.

    Find the sum from n=2 to 100 of M(n).

URL: https://projecteuler.net/problem=563
"""
from typing import Any

euler_problem: int = 563
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {}, 'answer': None},
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

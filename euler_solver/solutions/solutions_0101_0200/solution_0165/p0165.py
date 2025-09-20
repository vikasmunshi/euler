#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 165: Intersections.

Problem Statement:
    A segment is uniquely defined by its two endpoints. By considering two line
    segments in plane geometry there are three possibilities: the segments have
    zero points, one point, or infinitely many points in common.
    When two segments have exactly one point in common that common point may be
    an endpoint of one or both segments. If a common point of two segments is
    not an endpoint of either segment it is an interior point of both segments.
    We call a common point T of two segments L1 and L2 a true intersection point
    of L1 and L2 if T is the only common point of L1 and L2 and T is an interior
    point of both segments.
    Consider the three segments L1, L2 and L3:
        L1: (27, 44) to (12, 32)
        L2: (46, 53) to (17, 62)
        L3: (46, 70) to (22, 40)
    It can be verified that L2 and L3 have a true intersection point. As one
    of the end points of L3, namely (22,40), lies on L1 this is not considered
    to be a true intersection. L1 and L2 have no common point. So among these
    three segments there is one true intersection point.
    Now let us do the same for 5000 line segments. To this end we generate
    20000 numbers using the Blum Blum Shub pseudo-random generator:
        s0 = 290797
        s_{n+1} = s_n * s_n mod 50515093
        t_n = s_n mod 500
    To create each line segment we use four consecutive numbers t_n. That is,
    the first line segment is given by (t1, t2) to (t3, t4). The first four
    numbers computed are 27, 144, 12 and 232 giving the first segment
    (27,144) to (12,232).
    How many distinct true intersection points are found among the 5000 line
    segments?

URL: https://projecteuler.net/problem=165
"""
from typing import Any

euler_problem: int = 165
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'num_segments': 3}, 'answer': None},
    {'category': 'main', 'input': {'num_segments': 5000}, 'answer': None},
    {'category': 'extra', 'input': {'num_segments': 10000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

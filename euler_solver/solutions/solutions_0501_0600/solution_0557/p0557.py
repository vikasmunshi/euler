#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 557: Cutting Triangles.

Problem Statement:
    A triangle is cut into four pieces by two straight lines, each starting at one vertex
    and ending on the opposite edge. This results in forming three smaller triangular
    pieces, and one quadrilateral. If the original triangle has an integral area, it is
    often possible to choose cuts such that all of the four pieces also have integral area.
    For example, the diagram below shows a triangle of area 55 that has been cut in this way.

    Representing the areas as a, b, c and d, in the example above, the individual areas
    are a = 22, b = 8, c = 11 and d = 14. It is also possible to cut a triangle of area 55
    such that a = 20, b = 2, c = 24, d = 9.

    Define a triangle cutting quadruple (a, b, c, d) as a valid integral division of a
    triangle, where a is the area of the triangle between the two cut vertices, d is the
    area of the quadrilateral and b and c are the areas of the two other triangles, with
    the restriction that b ≤ c. The two solutions described above are (22,8,11,14) and
    (20,2,24,9). These are the only two possible quadruples that have a total area of 55.

    Define S(n) as the sum of the area of the uncut triangles represented by all valid
    quadruples with a+b+c+d ≤ n.
    For example, S(20) = 259.

    Find S(10000).

URL: https://projecteuler.net/problem=557
"""
from typing import Any

euler_problem: int = 557
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 20}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

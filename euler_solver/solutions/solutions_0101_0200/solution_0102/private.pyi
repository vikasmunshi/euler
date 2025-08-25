#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 102: Triangle Containment.

Problem Statement:
    Three distinct points are plotted at random on a Cartesian plane, for which
    -1000 ≤ x, y ≤ 1000, such that a triangle is formed.

    Consider the following two triangles:

        A(-340,495), B(-153,-910), C(835,-947)
        X(-175,41), Y(-421,-714), Z(574,-645)

    It can be verified that triangle ABC contains the origin, whereas triangle XYZ 
    does not.

    Using triangles.txt (right click and 'Save Link/Target As...'), a 27K text file 
    containing the co-ordinates of one thousand "random" triangles, find the number 
    of triangles for which the interior contains the origin.

Solution Approach:
    Use computational geometry to determine if the origin lies inside each triangle.
    Key idea: use vector cross products or area comparisons to check if origin is 
    inside the triangle. Efficiently process all 1000 triangles from the file.
    Time complexity O(n) for n=1000 triangles is feasible.

Answer: ...
URL: https://projecteuler.net/problem=102
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.maths.two_d_shapes import Point2D, Polygon2D
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 102
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'preliminary', 'input': {'triangles_file_url': ''}},
    {'category': 'main',
     'input': {'triangles_file_url': 'https://projecteuler.net/resources/documents/0102_triangles.txt'}}
]

points: dict[str, Point2D] = {'A': Point2D(-340, 495), 'B': Point2D(-153, -910), 'C': Point2D(835, -947),
                              'X': Point2D(-175, 41), 'Y': Point2D(-421, -714), 'Z': Point2D(574, -645), }
example_triangles: list[Polygon2D] = [Polygon2D(vertices=(points['A'], points['B'], points['C'],)),
                                      Polygon2D(vertices=(points['X'], points['Y'], points['Z'],)), ]


@register_solution(euler_problem=euler_problem, max_test_case=None)
def solve_triangle_containment_p0102_s0(*, triangles_file_url: str) -> int:
    ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))

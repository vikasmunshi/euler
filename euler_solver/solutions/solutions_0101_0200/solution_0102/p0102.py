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

URL: https://projecteuler.net/problem=102
"""
from typing import Any

euler_problem: int = 102
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'file_url': ''},
     'answer': None},
    {'category': 'main', 'input': {'file_url': 'https://projecteuler.net/resources/documents/0102_triangles.txt'},
     'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

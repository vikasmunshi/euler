#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 139: Pythagorean Tiles.

Problem Statement:
    Let (a, b, c) represent the three sides of a right angle triangle
    with integral length sides. It is possible to place four such triangles
    together to form a square with side length c.

    For example, (3, 4, 5) triangles can be placed together to form a 5 by 5
    square with a 1 by 1 hole in the middle, and the 5 by 5 square can be
    tiled with twenty-five 1 by 1 squares.

    However, if (5, 12, 13) triangles were used then the hole would measure
    7 by 7 and these could not be used to tile the 13 by 13 square.

    Given that the perimeter of the right triangle is less than
    one-hundred million, how many Pythagorean triangles would allow such a
    tiling to take place?

URL: https://projecteuler.net/problem=139
"""
from typing import Any

euler_problem: int = 139
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_perimeter': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_perimeter': 100000000}, 'answer': None},
]
encrypted: str = (
    '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'
    '4jqREmNi1OOErofPV8SEQQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

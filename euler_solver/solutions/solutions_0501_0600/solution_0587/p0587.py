#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 587: Concave Triangle.

Problem Statement:
    A square is drawn around a circle as shown in the diagram below on the left.
    We shall call the blue shaded region the L-section.
    A line is drawn from the bottom left of the square to the top right as shown
    in the diagram on the right.
    We shall call the orange shaded region a concave triangle.

    It should be clear that the concave triangle occupies exactly half of the L-section.

    Two circles are placed next to each other horizontally, a rectangle is drawn
    around both circles, and a line is drawn from the bottom left to the top right
    as shown in the diagram below.

    This time the concave triangle occupies approximately 36.46% of the L-section.

    If n circles are placed next to each other horizontally, a rectangle is drawn
    around the n circles, and a line is drawn from the bottom left to the top right,
    then it can be shown that the least value of n for which the concave triangle
    occupies less than 10% of the L-section is n = 15.

    What is the least value of n for which the concave triangle occupies less
    than 0.1% of the L-section?

URL: https://projecteuler.net/problem=587
"""
from typing import Any

euler_problem: int = 587
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_n': 2}, 'answer': None},
    {'category': 'main', 'input': {'max_n': 15}, 'answer': None},
    {'category': 'extra', 'input': {'max_n': 100}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

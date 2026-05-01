#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 695: Random Rectangles.

Problem Statement:
    Three points, P1, P2 and P3, are randomly selected within a unit square.
    Consider the three rectangles with sides parallel to the sides of the unit
    square and a diagonal that is one of the three line segments P1P2, P1P3 or
    P2P3.

    We are interested in the rectangle with the second biggest area. In the
    example above that happens to be the green rectangle defined with the
    diagonal P2P3.

    Find the expected value of the area of the second biggest of the three
    rectangles. Give your answer rounded to 10 digits after the decimal point.

URL: https://projecteuler.net/problem=695
"""
from typing import Any

euler_problem: int = 695
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

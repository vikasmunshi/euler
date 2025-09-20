#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 177: Integer Angled Quadrilaterals.

Problem Statement:
    Let ABCD be a convex quadrilateral, with diagonals AC and BD. At each
    vertex the diagonal makes an angle with each of the two sides, creating
    eight corner angles.

    For example, at vertex A, the two angles are CAD, CAB.

    We call such a quadrilateral for which all eight corner angles have
    integer values when measured in degrees an "integer angled quadrilateral".
    An example of an integer angled quadrilateral is a square, where all eight
    corner angles are 45°.

    Another example is given by DAC = 20°, BAC = 60°, ABD = 50°, CBD = 30°,
    BCA = 40°, DCA = 30°, CDB = 80°, ADB = 50°.

    What is the total number of non-similar integer angled quadrilaterals?

    Note: In your calculations you may assume that a calculated angle is
    integral if it is within a tolerance of 10^-9 of an integer value.

URL: https://projecteuler.net/problem=177
"""
from typing import Any

euler_problem: int = 177
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'bOuogAXwvMQ+kcAFr9f8B/s8LeRk0jXTE3RqvQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 144: Laser Beam Reflections.

Problem Statement:
    In laser physics, a "white cell" is a mirror system that acts as a delay
    line for the laser beam. The beam enters the cell, bounces around on the
    mirrors, and eventually works its way back out.
    The specific white cell we will be considering is an ellipse with the
    equation 4x^2 + y^2 = 100.
    The section corresponding to -0.01 <= x <= +0.01 at the top is missing,
    allowing the light to enter and exit through the hole.
    The light beam in this problem starts at the point (0.0,10.1) just outside
    the white cell, and the beam first impacts the mirror at (1.4,-9.6).
    Each time the laser beam hits the surface of the ellipse, it follows the
    usual law of reflection: angle of incidence equals angle of reflection.
    The slope m of the tangent line at any point (x,y) of the ellipse is
    m = -4x/y. The normal line is perpendicular to this tangent line.
    The animation in the problem shows the first 10 reflections of the beam.
    How many times does the beam hit the internal surface of the white cell
    before exiting through the gap at the top?

URL: https://projecteuler.net/problem=144
"""
from typing import Any

euler_problem: int = 144
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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 583: Heron Envelopes.

Problem Statement:
    A standard envelope shape is a convex figure consisting of an isosceles triangle
    (the flap) placed on top of a rectangle. An example of an envelope with integral
    sides is shown below. Note that to form a sensible envelope, the perpendicular
    height of the flap (BCD) must be smaller than the height of the rectangle (ABDE).

    In the envelope illustrated, not only are all the sides integral, but also all
    the diagonals (AC, AD, BD, BE, and CE) are integral too. Let us call an envelope
    with these properties a Heron envelope.

    Let S(p) be the sum of the perimeters of all the Heron envelopes with a perimeter
    less than or equal to p.

    You are given that S(10^4) = 884680. Find S(10^7).

URL: https://projecteuler.net/problem=583
"""
from typing import Any

euler_problem: int = 583
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'wMp0MowfbX3u2UT2'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 607: Marsh Crossing.

Problem Statement:
    Frodo and Sam need to travel 100 leagues due East from point A to point B. On normal
    terrain, they can cover 10 leagues per day, and so the journey would take 10 days.
    However, their path is crossed by a long marsh which runs exactly South-West to
    North-East, and walking through the marsh will slow them down. The marsh is 50 leagues
    wide at all points, and the mid-point of AB is located in the middle of the marsh.

    The marsh consists of 5 distinct regions, each 10 leagues across, as shown by the
    shading in the map. The strip closest to point A is relatively light marsh, and can
    be crossed at a speed of 9 leagues per day. However, each strip becomes progressively
    harder to navigate, the speeds going down to 8, 7, 6 and finally 5 leagues per day for
    the final region of marsh, before it ends and the terrain becomes easier again, with
    the speed going back to 10 leagues per day.

    If Frodo and Sam were to head directly East for point B, they would travel exactly 100
    leagues, and the journey would take approximately 13.4738 days. However, this time
    can be shortened if they deviate from the direct path.

    Find the shortest possible time required to travel from point A to B, and give your
    answer in days, rounded to 10 decimal places.

URL: https://projecteuler.net/problem=607
"""
from typing import Any

euler_problem: int = 607
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'Al1+BGjyZJgp3NqE'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

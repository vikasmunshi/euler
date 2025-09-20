#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 373: Circumscribed Circles.

Problem Statement:
    Every triangle has a circumscribed circle that goes through the three
    vertices. Consider all integer sided triangles for which the radius of
    the circumscribed circle is integral as well.

    Let S(n) be the sum of the radii of the circumscribed circles of all such
    triangles for which the radius does not exceed n.

    S(100)=4950 and S(1200)=1653605.

    Find S(10^7).

URL: https://projecteuler.net/problem=373
"""
from typing import Any

euler_problem: int = 373
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1200}, 'answer': None},
]
encrypted: str = (
    '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'
    'Rs6t0TS2d+g='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 410: Circle and Tangent Line.

Problem Statement:
    Let C be the circle with radius r, x^2 + y^2 = r^2. We choose two points P(a, b)
    and Q(-a, c) so that the line passing through P and Q is tangent to C.

    For example, the quadruplet (r, a, b, c) = (2, 6, 2, -7) satisfies this property.

    Let F(R, X) be the number of the integer quadruplets (r, a, b, c) with this property,
    and with 0 < r ≤ R and 0 < a ≤ X.

    We can verify that F(1, 5) = 10, F(2, 10) = 52 and F(10, 100) = 3384.
    Find F(10^8, 10^9) + F(10^9, 10^8).

URL: https://projecteuler.net/problem=410
"""
from typing import Any

euler_problem: int = 410
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_r': 1, 'max_a': 5}, 'answer': None},
    {'category': 'main', 'input': {'max_r': 100000000, 'max_a': 1000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_r': 1000000000, 'max_a': 100000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'dwHeYDLotroOzPIwFIHDaTz20CdaH05b'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

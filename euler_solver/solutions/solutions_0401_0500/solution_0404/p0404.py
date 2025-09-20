#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 404: Crisscross Ellipses.

Problem Statement:
    E_a is an ellipse with an equation of the form x^2 + 4y^2 = 4a^2.
    E_a' is the rotated image of E_a by θ degrees counterclockwise around
    the origin O(0, 0) for 0° < θ < 90°.

    b is the distance to the origin of the two intersection points closest
    to the origin and c is the distance of the two other intersection points.
    We call an ordered triplet (a, b, c) a canonical ellipsoidal triplet if
    a, b and c are positive integers.
    For example, (209, 247, 286) is a canonical ellipsoidal triplet.

    Let C(N) be the number of distinct canonical ellipsoidal triplets (a, b, c)
    for a ≤ N.
    It can be verified that C(10^3) = 7, C(10^4) = 106 and C(10^6) = 11845.

    Find C(10^17).

URL: https://projecteuler.net/problem=404
"""
from typing import Any

euler_problem: int = 404
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'woCzMQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

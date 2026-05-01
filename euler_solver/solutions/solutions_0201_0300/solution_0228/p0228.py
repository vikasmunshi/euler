#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 228: Minkowski Sums.

Problem Statement:
    Let S_n be the regular n-sided polygon - or shape - whose vertices v_k (k =
    1, 2, ..., n) have coordinates:
        x_k = cos((2k - 1)/n × 180°)
        y_k = sin((2k - 1)/n × 180°)

    Each S_n is to be interpreted as a filled shape consisting of all points
    on the perimeter and in the interior.

    The Minkowski sum, S + T, of two shapes S and T is the result of adding
    every point in S to every point in T, where point addition is performed
    coordinate-wise: (u, v) + (x, y) = (u + x, v + y).

    For example, the sum of S_3 and S_4 is the six-sided shape shown in the
    problem statement.

    How many sides does S_1864 + S_1865 + ... + S_1909 have?

URL: https://projecteuler.net/problem=228
"""
from typing import Any

euler_problem: int = 228
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'start': 3, 'end': 4}, 'answer': None},
    {'category': 'main', 'input': {'start': 1864, 'end': 1909}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

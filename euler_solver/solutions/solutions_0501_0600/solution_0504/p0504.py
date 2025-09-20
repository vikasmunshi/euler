#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 504: Square on the Inside.

Problem Statement:
    Let ABCD be a quadrilateral whose vertices are lattice points lying on the
    coordinate axes as follows:

    A(a, 0), B(0, b), C(-c, 0), D(0, -d), where 1 ≤ a, b, c, d ≤ m and a, b, c,
    d, m are integers.

    It can be shown that for m = 4 there are exactly 256 valid ways to construct
    ABCD. Of these 256 quadrilaterals, 42 of them strictly contain a square number
    of lattice points.

    How many quadrilaterals ABCD strictly contain a square number of lattice points
    for m = 100?

URL: https://projecteuler.net/problem=504
"""
from typing import Any

euler_problem: int = 504
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 4}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100}, 'answer': None},
]
encrypted: str = (
    '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'
    'DxOnblTfoMiyrOgWxXTwog=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 398: Cutting Rope.

Problem Statement:
    Inside a rope of length n, n - 1 points are placed with distance 1 from
    each other and from the endpoints. Among these points, we choose m - 1
    points at random and cut the rope at these points to create m segments.

    Let E(n, m) be the expected length of the second-shortest segment.
    For example, E(3, 2) = 2 and E(8, 3) = 16/7. Note that if multiple
    segments have the same shortest length the length of the second-shortest
    segment is defined as the same as the shortest length.

    Find E(10^7, 100). Give your answer rounded to 5 decimal places behind
    the decimal point.

URL: https://projecteuler.net/problem=398
"""
from typing import Any

euler_problem: int = 398
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3, 'm': 2}, 'answer': None},
    {'category': 'main', 'input': {'n': 10000000, 'm': 100}, 'answer': None},
    {'category': 'extra', 'input': {'n': 100000, 'm': 100}, 'answer': None},
]
encrypted: str = (
    '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'
    'JEgqEA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

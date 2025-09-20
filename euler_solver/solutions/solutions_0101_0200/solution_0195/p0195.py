#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 195: 60-degree Triangle Inscribed Circles.

Problem Statement:
    Let's call an integer sided triangle with exactly one angle of 60 degrees a
    60-degree triangle.
    Let r be the radius of the inscribed circle of such a 60-degree triangle.

    There are 1234 60-degree triangles for which r <= 100.
    Let T(n) be the number of 60-degree triangles for which r <= n, so
    T(100) = 1234, T(1000) = 22767, and T(10000) = 359912.

    Find T(1053779).

URL: https://projecteuler.net/problem=195
"""
from typing import Any

euler_problem: int = 195
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1053779}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 2000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'Fe3tfXQ+k0PXo17x3lpAx/gdhxgpQJNWk9WGSg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

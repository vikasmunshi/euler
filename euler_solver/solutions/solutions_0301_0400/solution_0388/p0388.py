#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 388: Distinct Lines.

Problem Statement:
    Consider all lattice points (a,b,c) with 0 <= a,b,c <= N.
    From the origin O(0,0,0) all lines are drawn to the other lattice points.
    Let D(N) be the number of distinct such lines.

    You are given that D(10^6) = 831909254469114121.

    Find D(10^10). Give as your answer the first nine digits followed by the
    last nine digits.

URL: https://projecteuler.net/problem=388
"""
from typing import Any

euler_problem: int = 388
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

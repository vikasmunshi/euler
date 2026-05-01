#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 542: Geometric Progression with Maximum Sum.

Problem Statement:
    Let S(k) be the sum of three or more distinct positive integers having the
    following properties:
        - No value exceeds k.
        - The values form a geometric progression.
        - The sum is maximal.

    S(4) = 4 + 2 + 1 = 7
    S(10) = 9 + 6 + 4 = 19
    S(12) = 12 + 6 + 3 = 21
    S(1000) = 1000 + 900 + 810 + 729 = 3439

    Let T(n) = ∑_{k=4}^n (-1)^k S(k).
    T(1000) = 2268

    Find T(10^17).

URL: https://projecteuler.net/problem=542
"""
from typing import Any

euler_problem: int = 542
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

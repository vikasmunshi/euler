#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 546: The Floor's Revenge.

Problem Statement:
    Define f_k(n) = sum_{i=0}^n f_k(floor(i / k)) where f_k(0) = 1 and floor(x) is the floor function.

    For example, f_5(10) = 18, f_7(100) = 1003, and f_2(10^3) = 264830889564.

    Find (sum_{k=2}^{10} f_k(10^14)) mod (10^9 + 7).

URL: https://projecteuler.net/problem=546
"""
from typing import Any

euler_problem: int = 546
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'max_limit': 100000000000000, 'k_min': 2, 'k_max': 10}, 'answer': None},
]
encrypted: str = (
    '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'
    '6cQ9Hw5os4MC1OGxbAV2Agsk7Y2kjDAA'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

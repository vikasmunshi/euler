#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 660: Pandigital Triangles.

Problem Statement:
    We call an integer sided triangle n-pandigital if it contains one angle of 120
    degrees and, when the sides of the triangle are written in base n, together they
    use all n digits of that base exactly once.

    For example, the triangle (217, 248, 403) is 9-pandigital because it contains
    one angle of 120 degrees and the sides written in base 9 are 261_9, 305_9, 487_9
    using each of the 9 digits of that base once.

    Find the sum of the largest sides of all n-pandigital triangles with 9 ≤ n ≤ 18.

URL: https://projecteuler.net/problem=660
"""
from typing import Any

euler_problem: int = 660
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

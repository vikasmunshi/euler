#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 428: Necklace of Circles.

Problem Statement:
    Let a, b and c be positive numbers.
    Let W, X, Y, Z be four collinear points where |WX| = a, |XY| = b, |YZ| = c and |WZ| = a + b + c.
    Let C_in be the circle having the diameter XY.
    Let C_out be the circle having the diameter WZ.

    The triplet (a, b, c) is called a necklace triplet if you can place k >= 3 distinct circles
    C_1, C_2, ..., C_k such that:
        • C_i has no common interior points with any C_j for 1 <= i, j <= k and i != j,
        • C_i is tangent to both C_in and C_out for 1 <= i <= k,
        • C_i is tangent to C_{i+1} for 1 <= i < k, and
        • C_k is tangent to C_1.

    For example, (5, 5, 5) and (4, 3, 21) are necklace triplets, while it can be shown that (2, 2, 5) is not.

    Let T(n) be the number of necklace triplets (a, b, c) such that a, b and c are positive integers,
    and b <= n.
    For example, T(1) = 9, T(20) = 732 and T(3000) = 438106.

    Find T(1000000000).

URL: https://projecteuler.net/problem=428
"""
from typing import Any

euler_problem: int = 428
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_b': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_b': 1000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'UH4Ab3fXSIqFkKQ/bebflA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 299: Three Similar Triangles.

Problem Statement:
    Four points with integer coordinates are selected:
    A(a, 0), B(b, 0), C(0, c) and D(0, d), with 0 < a < b and 0 < c < d.
    Point P, also with integer coordinates, is chosen on the line AC so that
    the three triangles ABP, CDP and BDP are all similar.

    It is easy to prove that the three triangles can be similar only if a = c.
    So, given that a = c, we seek triplets (a, b, d) such that at least one
    integer point P on AC makes ABP, CDP and BDP all similar.

    Example: (a, b, d) = (2, 3, 4) admits P(1,1). Triplets (2,3,4) and (2,4,3)
    are distinct even though they may share the same P.

    If b + d < 100 there are 92 distinct triplets.
    If b + d < 100000 there are 320471 distinct triplets.
    If b + d < 100000000, how many distinct triplets (a, b, d) are there?

URL: https://projecteuler.net/problem=299
"""
from typing import Any

euler_problem: int = 299
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

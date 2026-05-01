#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 276: Primitive Triangles.

Problem Statement:
    Consider the triangles with integer sides a, b and c with a <= b <= c.
    An integer sided triangle (a,b,c) is called primitive if gcd(a, b, c) = 1.
    How many primitive integer sided triangles exist with a perimeter not
    exceeding 10^7?

URL: https://projecteuler.net/problem=276
"""
from typing import Any

euler_problem: int = 276
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 20000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

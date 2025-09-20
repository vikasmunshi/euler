#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 476: Circle Packing II.

Problem Statement:
    Let R(a, b, c) be the maximum area covered by three non-overlapping circles
    inside a triangle with edge lengths a, b and c.

    Let S(n) be the average value of R(a, b, c) over all integer triplets (a, b, c)
    such that 1 <= a <= b <= c < a + b <= n.

    You are given S(2) = R(1, 1, 1) approximately 0.31998, S(5) approximately 1.25899.

    Find S(1803) rounded to 5 decimal places behind the decimal point.

URL: https://projecteuler.net/problem=476
"""
from typing import Any

euler_problem: int = 476
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 5}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1803}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

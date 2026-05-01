#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 224: Almost Right-angled Triangles II.

Problem Statement:
    Let us call an integer sided triangle with sides a <= b <= c barely obtuse
    if the sides satisfy
    a^2 + b^2 = c^2 - 1.

    How many barely obtuse triangles are there with perimeter <= 75,000,000?

URL: https://projecteuler.net/problem=224
"""
from typing import Any

euler_problem: int = 224
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 75000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 100000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'nPMaCDLbpk4='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

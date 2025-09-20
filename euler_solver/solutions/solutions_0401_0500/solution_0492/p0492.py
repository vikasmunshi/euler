#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 492: Exploding Sequence.

Problem Statement:
    Define the sequence a_1, a_2, a_3, ... as:
        a_1 = 1
        a_{n+1} = 6 a_n^2 + 10 a_n + 3 for n ≥ 1.

    Examples:
        a_3 = 2359
        a_6 = 269221280981320216750489044576319
        a_6 mod 1000000007 = 203064689
        a_100 mod 1000000007 = 456482974

    Define B(x, y, n) as the sum of (a_n mod p) for every prime p such that x ≤ p ≤ x + y.

    Examples:
        B(10^9, 10^3, 10^3) = 23674718882
        B(10^9, 10^3, 10^{15}) = 20731563854

    Find B(10^9, 10^7, 10^{15}).

URL: https://projecteuler.net/problem=492
"""
from typing import Any

euler_problem: int = 492
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'x': 1000000000, 'y': 1000, 'n': 1000}, 'answer': None},
    {'category': 'main', 'input': {'x': 1000000000, 'y': 10000000, 'n': 1000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

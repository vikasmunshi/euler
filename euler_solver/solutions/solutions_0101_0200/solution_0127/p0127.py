#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 127: abc-hits.

Problem Statement:
    The radical of n, rad(n), is the product of distinct prime factors of n.
    For example, 504 = 2^3 * 3^2 * 7, so rad(504) = 2 * 3 * 7 = 42.

    We shall define the triplet of positive integers (a, b, c) to be an abc-hit if:
        gcd(a, b) = gcd(a, c) = gcd(b, c) = 1
        a < b
        a + b = c
        rad(abc) < c

    For example, (5, 27, 32) is an abc-hit because:
        gcd(5,27) = gcd(5,32) = gcd(27,32) = 1
        5 < 27
        5 + 27 = 32
        rad(4320) = 30 < 32

    It turns out that abc-hits are rare and there are only thirty-one abc-hits
    for c < 1000, with sum c = 12523.

    Find sum c for c < 120000.

URL: https://projecteuler.net/problem=127
"""
from typing import Any

euler_problem: int = 127
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 120000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 200000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

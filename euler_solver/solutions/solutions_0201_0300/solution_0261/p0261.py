#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 261: Pivotal Square Sums.

Problem Statement:
    Let us call a positive integer k a square-pivot, if there is a pair of
    integers m > 0 and n >= k, such that the sum of the (m+1) consecutive
    squares up to k equals the sum of the m consecutive squares from (n+1)
    on:
    (k - m)^2 + ... + k^2 = (n + 1)^2 + ... + (n + m)^2.

    Some small square-pivots are
    4:  3^2 + 4^2 = 5^2
    21: 20^2 + 21^2 = 29^2
    24: 21^2 + 22^2 + 23^2 + 24^2 = 25^2 + 26^2 + 27^2
    110: 108^2 + 109^2 + 110^2 = 133^2 + 134^2

    Find the sum of all distinct square-pivots <= 10^10.

URL: https://projecteuler.net/problem=261
"""
from typing import Any

euler_problem: int = 261
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 100000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'aC/P+24zlYNY2UuN'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

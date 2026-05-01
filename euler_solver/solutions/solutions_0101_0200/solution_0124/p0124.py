#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 124: Ordered Radicals.

Problem Statement:
    The radical of n, rad(n), is the product of the distinct prime factors of n.
    For example, 504 = 2^3 * 3^2 * 7, so rad(504) = 2 * 3 * 7 = 42.

    If we calculate rad(n) for 1 <= n <= 10, then sort the integers by rad(n),
    and break ties by the value of n, we obtain a sorted sequence of n-values.
    Let E(k) be the k-th element in that sorted n column; for example E(4) = 8
    and E(6) = 9.

    If rad(n) is sorted for 1 <= n <= 100000, find E(10000).

URL: https://projecteuler.net/problem=124
"""
from typing import Any

euler_problem: int = 124
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10, 'k': 4}, 'answer': None},
    {'category': 'dev', 'input': {'max_limit': 10, 'k': 6}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000, 'k': 10000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 200000, 'k': 20000}, 'answer': None},
]
encrypted: str = (
    '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'
    '3aau0lYvRl6txJkDxPYQqA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

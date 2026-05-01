#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 343: Fractional Sequences.

Problem Statement:
    For any positive integer k, a finite sequence a_i of fractions x_i/y_i is
    defined by:
    a_1 = 1/k
    a_i = (x_{i-1} + 1) / (y_{i-1} - 1) reduced to lowest terms for i > 1.
    When a_i reaches some integer n the sequence stops (that is, when y_i = 1).
    Define f(k) = n.

    For example, for k = 20:
    1/20 -> 2/19 -> 3/18 = 1/6 -> 2/5 -> 3/4 -> 4/3 -> 5/2 -> 6/1 = 6

    So f(20) = 6.

    Also f(1) = 1, f(2) = 2, f(3) = 1 and sum f(k^3) = 118937 for 1 <= k <= 100.

    Find sum f(k^3) for 1 <= k <= 2 * 10^6.

URL: https://projecteuler.net/problem=343
"""
from typing import Any

euler_problem: int = 343
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 2000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 5000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'JdGMHQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 397: Triangle on Parabola.

Problem Statement:
    On the parabola y = x^2/k, three points A(a, a^2/k), B(b, b^2/k) and C(c, c^2/k)
    are chosen.

    Let F(K, X) be the number of the integer quadruplets (k, a, b, c) such that at
    least one angle of the triangle ABC is 45-degree, with 1 <= k <= K and -X <= a
    < b < c <= X.

    For example, F(1, 10) = 41 and F(10, 100) = 12492.
    Find F(10^6, 10^9).

URL: https://projecteuler.net/problem=397
"""
from typing import Any

euler_problem: int = 397
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_k': 1, 'max_x': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_k': 1000000, 'max_x': 1000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_k': 10, 'max_x': 100}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

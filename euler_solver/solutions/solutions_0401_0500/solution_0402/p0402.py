#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 402: Integer-valued Polynomials.

Problem Statement:
    It can be shown that the polynomial n^4 + 4n^3 + 2n^2 + 5n is a multiple of 6 for every
    integer n. It can also be shown that 6 is the largest integer satisfying this property.

    Define M(a, b, c) as the maximum m such that n^4 + an^3 + bn^2 + cn is a multiple of m
    for all integers n. For example, M(4, 2, 5) = 6.

    Also, define S(N) as the sum of M(a, b, c) for all 0 < a, b, c ≤ N.

    We can verify that S(10) = 1972 and S(10000) = 2024258331114.

    Let F_k be the Fibonacci sequence:
    F_0 = 0, F_1 = 1 and
    F_k = F_{k-1} + F_{k-2} for k ≥ 2.

    Find the last 9 digits of the sum of S(F_k) for 2 ≤ k ≤ 1234567890123.

URL: https://projecteuler.net/problem=402
"""
from typing import Any

euler_problem: int = 402
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'k_start': 2, 'k_end': 1234567890123}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

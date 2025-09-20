#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 738: Counting Ordered Factorisations.

Problem Statement:
    Define d(n,k) to be the number of ways to write n as a product of k ordered
    integers

        n = x1 × x2 × x3 × ... × xk     with 1 ≤ x1 ≤ x2 ≤ ... ≤ xk

    Further define D(N,K) to be the sum of d(n,k) for 1 ≤ n ≤ N and 1 ≤ k ≤ K.

    You are given that D(10, 10) = 153 and D(100, 100) = 35384.

    Find D(10^10, 10^10) giving your answer modulo 1000000007.

URL: https://projecteuler.net/problem=738
"""
from typing import Any

euler_problem: int = 738
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'N': 10, 'K': 10}, 'answer': None},
    {'category': 'main', 'input': {'N': 10000000000, 'K': 10000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'ZxOQVsAECLo='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

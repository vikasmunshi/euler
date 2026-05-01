#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 485: Maximum Number of Divisors.

Problem Statement:
    Let d(n) be the number of divisors of n.
    Let M(n,k) be the maximum value of d(j) for n <= j <= n+k-1.
    Let S(u,k) be the sum of M(n,k) for 1 <= n <= u-k+1.

    You are given that S(1000,10) = 17176.

    Find S(100000000, 100000).

URL: https://projecteuler.net/problem=485
"""
from typing import Any

euler_problem: int = 485
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'u': 1000, 'k': 10}, 'answer': None},
    {'category': 'main', 'input': {'u': 100000000, 'k': 100000}, 'answer': None},
]
encrypted: str = (
    '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'
    'qJXssZKXQi+lwYzl'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

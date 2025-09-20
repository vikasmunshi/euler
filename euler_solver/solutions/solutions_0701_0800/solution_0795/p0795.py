#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 795: Alternating GCD Sum.

Problem Statement:
    For a positive integer n, the function g(n) is defined as
        g(n) = sum from i=1 to n of (-1)^i * gcd(n, i^2).

    For example, g(4) = -gcd(4, 1^2) + gcd(4, 2^2) - gcd(4, 3^2) + gcd(4, 4^2)
    = -1 + 4 - 1 + 4 = 6.
    You are also given g(1234) = 1233.

    Let G(N) = sum from n=1 to N of g(n). You are given G(1234) = 2194708.

    Find G(12345678).

URL: https://projecteuler.net/problem=795
"""
from typing import Any

euler_problem: int = 795
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 12345678}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

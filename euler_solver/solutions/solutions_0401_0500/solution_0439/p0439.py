#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 439: Sum of Sum of Divisors.

Problem Statement:
    Let d(k) be the sum of all divisors of k.
    We define the function S(N) = sum from i=1 to N of sum from j=1 to N of d(i * j).
    For example, S(3) = d(1) + d(2) + d(3) + d(2) + d(4) + d(6) + d(3) + d(6) + d(9) = 59.

    You are given that S(10^3) = 563576517282 and S(10^5) mod 10^9 = 215766508.
    Find S(10^11) mod 10^9.

URL: https://projecteuler.net/problem=439
"""
from typing import Any

euler_problem: int = 439
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'UCHbOg6HGXCXpDEqf3rg6gJrKzQ='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

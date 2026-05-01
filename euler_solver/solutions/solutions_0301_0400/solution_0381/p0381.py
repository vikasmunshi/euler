#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 381: (prime-k) Factorial.

Problem Statement:
    For a prime p let S(p) = (sum (p-k)!) mod p for 1 <= k <= 5.

    For example, if p = 7,
    (7-1)! + (7-2)! + (7-3)! + (7-4)! + (7-5)!
    = 6! + 5! + 4! + 3! + 2!
    = 720 + 120 + 24 + 6 + 2 = 872.
    As 872 mod 7 = 4, S(7) = 4.

    It can be verified that sum S(p) = 480 for 5 <= p < 100.

    Find sum S(p) for 5 <= p < 10^8.

URL: https://projecteuler.net/problem=381
"""
from typing import Any

euler_problem: int = 381
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

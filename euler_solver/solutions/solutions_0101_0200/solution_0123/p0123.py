#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 123: Prime Square Remainders.

Problem Statement:
    Let p_n be the nth prime: 2, 3, 5, 7, 11, ..., and let r be the remainder
    when (p_n - 1)^n + (p_n + 1)^n is divided by p_n^2.

    For example, when n = 3, p_3 = 5, and 4^3 + 6^3 = 280 ≡ 5 mod 25.

    The least value of n for which the remainder first exceeds 10^9 is 7037.

    Find the least value of n for which the remainder first exceeds 10^10.

URL: https://projecteuler.net/problem=123
"""
from typing import Any

euler_problem: int = 123
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'threshold': 1_000_000_000}, 'answer': None},
    {'category': 'main', 'input': {'threshold': 10_000_000_000}, 'answer': None},
    {'category': 'extra', 'input': {'threshold': 100_000_000_000}, 'answer': None},
]
encrypted: str = (
    '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'
    'nxDhYcwqi5OS1njmAWmlctVSCvYnPWLxINx3nw=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

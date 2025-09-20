#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 443: GCD Sequence.

Problem Statement:
    Let g(n) be a sequence defined as follows:
    g(4) = 13,
    g(n) = g(n-1) + gcd(n, g(n-1)) for n > 4.

    The first few values are:
    n:  4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, ...
    g(n): 13, 14, 16, 17, 18, 27, 28, 29, 30, 31, 32, 33, 34, 51, 54, 55, 60, ...

    You are given that g(1 000) = 2524 and g(1 000 000) = 2624152.

    Find g(10^15).

URL: https://projecteuler.net/problem=443
"""
from typing import Any

euler_problem: int = 443
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 10}, 'answer': None},
    {'category': 'main', 'input': {'n': 1000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'ENwdQg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 754: Product of Gauss Factorials.

Problem Statement:
    The Gauss Factorial of a number n is defined as the product of all positive numbers
    less than or equal to n that are relatively prime to n. For example g(10) =
    1 × 3 × 7 × 9 = 189.

    Also we define
        G(n) = product of g(i) for i = 1 to n.

    You are given G(10) = 23044331520000.

    Find G(10^8). Give your answer modulo 1000000007.

URL: https://projecteuler.net/problem=754
"""
from typing import Any

euler_problem: int = 754
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'o/GRji3CcYbEI86HhK7p0xkuxww='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

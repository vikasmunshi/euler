#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 760: Sum over Bitwise Operators.

Problem Statement:
    Define
        g(m,n) = (m XOR n) + (m OR n) + (m AND n)
    where XOR, OR and AND are the bitwise operators.

    Also set
        G(N) = sum for n=0 to N of (sum for k=0 to n of g(k, n-k))

    For example, G(10) = 754 and G(10^2) = 583766.

    Find G(10^18). Give your answer modulo 1,000,000,007.

URL: https://projecteuler.net/problem=760
"""
from typing import Any

euler_problem: int = 760
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'opVVEJES6NUknQFmgMJFgvDo1+E='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

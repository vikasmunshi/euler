#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 608: Divisor Sums.

Problem Statement:
    Let D(m,n) = sum over divisors d of m of sum from k=1 to n of sigma_0(kd),
    where sigma_0(n) is the number of divisors of n.

    You are given D(3!, 10^2) = 3398 and D(4!, 10^6) = 268882292.

    Find D(200!, 10^12) modulo (10^9 + 7).

URL: https://projecteuler.net/problem=608
"""
from typing import Any

euler_problem: int = 608
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'m_factorial': 3, 'n': 100}, 'answer': None},
    {'category': 'main', 'input': {'m_factorial': 200, 'n': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

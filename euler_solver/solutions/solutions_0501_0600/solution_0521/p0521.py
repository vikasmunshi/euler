#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 521: Smallest Prime Factor.

Problem Statement:
    Let smpf(n) be the smallest prime factor of n.
    smpf(91) = 7 because 91 = 7 x 13 and smpf(45) = 3 because 45 = 3 x 3 x 5.
    Let S(n) be the sum of smpf(i) for 2 ≤ i ≤ n.
    For example, S(100) = 1257.

    Find S(10^12) modulo 10^9.

URL: https://projecteuler.net/problem=521
"""
from typing import Any

euler_problem: int = 521
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'max_limit': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

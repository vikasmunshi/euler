#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 322: Binomial Coefficients Divisible by 10.

Problem Statement:
    Let T(m, n) be the number of the binomial coefficients C(i, n) that are
    divisible by 10 for n <= i < m (i, m and n are positive integers).
    You are given that T(10^9, 10^7-10) = 989697000.

    Find T(10^18, 10^12-10).

URL: https://projecteuler.net/problem=322
"""
from typing import Any

euler_problem: int = 322
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'m': 1000000000, 'n': 9999990}, 'answer': None},
    {'category': 'main', 'input': {'m': 1000000000000000000, 'n': 999999999990}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

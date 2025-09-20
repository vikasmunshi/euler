#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 145: Reversible Numbers.

Problem Statement:
    Some positive integers n have the property that the sum [n + reverse(n)]
    consists entirely of odd (decimal) digits. For instance, 36 + 63 = 99 and
    409 + 904 = 1313. We will call such numbers reversible; so 36, 63, 409,
    and 904 are reversible. Leading zeroes are not allowed in either n or
    reverse(n).

    There are 120 reversible numbers below one-thousand.

    How many reversible numbers are there below one-billion (10^9)?

URL: https://projecteuler.net/problem=145
"""
from typing import Any

euler_problem: int = 145
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'Xb1wgcsCpF6dH9sBi5iaug=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

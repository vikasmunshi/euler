#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 455: Powers with Trailing Digits.

Problem Statement:
    Let f(n) be the largest positive integer x less than 10^9 such that the last 9 digits
    of n^x form the number x (including leading zeros), or zero if no such integer exists.

    For example:
        f(4) = 411728896 (4^411728896 = ...490411728896)
        f(10) = 0
        f(157) = 743757 (157^743757 = ...567000743757)
        sum_{2 <= n <= 10^3} f(n) = 442530011399

    Find sum_{2 <= n <= 10^6} f(n).

URL: https://projecteuler.net/problem=455
"""
from typing import Any

euler_problem: int = 455
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

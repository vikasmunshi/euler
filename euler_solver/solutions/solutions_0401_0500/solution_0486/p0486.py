#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 486: Palindrome-containing Strings.

Problem Statement:
    Let F_5(n) be the number of strings s such that:
        s consists only of '0's and '1's,
        s has length at most n, and
        s contains a palindromic substring of length at least 5.

    For example, F_5(4) = 0, F_5(5) = 8, F_5(6) = 42 and F_5(11) = 3844.

    Let D(L) be the number of integers n such that 5 ≤ n ≤ L and F_5(n) is
    divisible by 87654321.

    For example, D(10^7) = 0 and D(5 · 10^9) = 51.

    Find D(10^18).

URL: https://projecteuler.net/problem=486
"""
from typing import Any

euler_problem: int = 486
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

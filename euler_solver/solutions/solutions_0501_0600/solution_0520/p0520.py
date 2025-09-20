#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 520: Simbers.

Problem Statement:
    We define a simber to be a positive integer in which any odd digit, if present,
    occurs an odd number of times, and any even digit, if present, occurs an even
    number of times.

    For example, 141221242 is a 9-digit simber because it has three 1's, four 2's
    and two 4's.

    Let Q(n) be the count of all simbers with at most n digits.

    You are given Q(7) = 287975 and Q(100) mod 1 000 000 123 = 123864868.

    Find (sum of Q(2^u) for 1 ≤ u ≤ 39) mod 1 000 000 123.

URL: https://projecteuler.net/problem=520
"""
from typing import Any

euler_problem: int = 520
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_digits': 7}, 'answer': None},
    {'category': 'main', 'input': {'max_digits': 1125899906842624}, 'answer': None},
    {'category': 'extra', 'input': {'max_digits': 512}, 'answer': None},
]
encrypted: str = (
    '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'
    '/nCPsg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

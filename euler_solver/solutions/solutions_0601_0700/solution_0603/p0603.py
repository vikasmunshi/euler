#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 603: Substring Sums of Prime Concatenations.

Problem Statement:
    Let S(n) be the sum of all contiguous integer-substrings that can be formed from
    the integer n. The substrings need not be distinct.

    For example, S(2024) = 2 + 0 + 2 + 4 + 20 + 02 + 24 + 202 + 024 + 2024 = 2304.

    Let P(n) be the integer formed by concatenating the first n primes together. For
    example, P(7) = 2357111317.

    Let C(n, k) be the integer formed by concatenating k copies of P(n) together. For
    example, C(7, 3) = 235711131723571113172357111317.

    Evaluate S(C(10^6, 10^12)) modulo (10^9 + 7).

URL: https://projecteuler.net/problem=603
"""
from typing import Any

euler_problem: int = 603
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'lCfjq9pGIXE='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

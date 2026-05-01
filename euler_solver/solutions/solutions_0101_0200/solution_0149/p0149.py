#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 149: Maximum-sum Subsequence.

Problem Statement:
    Looking at the table below, it is easy to verify that the maximum possible
    sum of adjacent numbers in any direction (horizontal, vertical, diagonal
    or anti-diagonal) is 16 (= 8 + 7 + 1).

    Now, let us repeat the search, but on a much larger scale:

    First, generate four million pseudo-random numbers using a specific form of
    what is known as a "Lagged Fibonacci Generator":

    For 1 <= k <= 55, s_k = [100003 - 200003 k + 300007 k^3] mod 1000000 - 500000.
    For 56 <= k <= 4000000, s_k = [s_{k-24} + s_{k-55} + 1000000] mod 1000000 - 500000.

    Thus, s_10 = -393027 and s_100 = 86613.

    The terms of s are then arranged in a 2000 x 2000 table, using the first
    2000 numbers to fill the first row, the next 2000 numbers the second row,
    and so on.

    Finally, find the greatest sum of (any number of) adjacent entries in any
    direction (horizontal, vertical, diagonal or anti-diagonal).

URL: https://projecteuler.net/problem=149
"""
from typing import Any

euler_problem: int = 149
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'size': 4}, 'answer': None},
    {'category': 'main', 'input': {'size': 2000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

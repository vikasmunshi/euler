#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 601: Divisibility Streaks.

Problem Statement:
    For every positive number n we define the function streak(n) = k as the smallest
    positive integer k such that n + k is not divisible by k + 1.
    E.g:
    13 is divisible by 1
    14 is divisible by 2
    15 is divisible by 3
    16 is divisible by 4
    17 is NOT divisible by 5
    So streak(13) = 4.
    Similarly:
    120 is divisible by 1
    121 is NOT divisible by 2
    So streak(120) = 1.

    Define P(s, N) to be the number of integers n, 1 < n < N, for which streak(n) = s.
    So P(3, 14) = 1 and P(6, 10^6) = 14286.

    Find the sum, as i ranges from 1 to 31, of P(i, 4^i).

URL: https://projecteuler.net/problem=601
"""
from typing import Any

euler_problem: int = 601
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_s': 6}, 'answer': None},
    {'category': 'main', 'input': {'max_s': 31}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

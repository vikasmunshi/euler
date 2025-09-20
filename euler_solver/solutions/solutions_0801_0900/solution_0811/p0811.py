#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 811: Bitwise Recursion.

Problem Statement:
    Let b(n) be the largest power of 2 that divides n. For example b(24) = 8.

    Define the recursive function:
        A(0) = 1
        A(2n) = 3A(n) + 5A(2n - b(n))  for n > 0
        A(2n+1) = A(n)
    and let H(t,r) = A((2^t + 1)^r).

    You are given H(3,2) = A(81) = 636056.

    Find H(10^14 + 31, 62). Give your answer modulo 1000062031.

URL: https://projecteuler.net/problem=811
"""
from typing import Any

euler_problem: int = 811
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'t': 100000000000031, 'r': 62}, 'answer': None},
]
encrypted: str = (
    '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'
    'JTJFzWdxR6MjCXbm6a5K9Utv60npodc+6QaSIw=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

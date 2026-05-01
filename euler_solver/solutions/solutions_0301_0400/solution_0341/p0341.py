#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 341: Golomb's Self-describing Sequence.

Problem Statement:
    The Golomb's self-describing sequence (G(n)) is the only nondecreasing
    sequence of natural numbers such that n appears exactly G(n) times in the
    sequence. The values of G(n) for the first few n are:
    n:  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 ...
    G:  1  2  2  3  3  4  4  4  5  5  5  6  6  6  6 ...
    You are given that G(10^3) = 86, G(10^6) = 6137.
    You are also given that sum G(n^3) = 153506976 for 1 <= n < 10^3.
    Find sum G(n^3) for 1 <= n < 10^6.

URL: https://projecteuler.net/problem=341
"""
from typing import Any

euler_problem: int = 341
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'dSnLbg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

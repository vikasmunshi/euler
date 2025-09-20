#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 822: Square the Smallest.

Problem Statement:
    A list initially contains the numbers 2, 3, ..., n.
    At each round, the smallest number in the list is replaced by its square.
    If there is more than one such number, then only one of them is replaced.

    For example, below are the first three rounds for n = 5:
    [2, 3, 4, 5] -> (1) [4, 3, 4, 5] -> (2) [4, 9, 4, 5] -> (3) [16, 9, 4, 5].

    Let S(n, m) be the sum of all numbers in the list after m rounds.

    For example, S(5, 3) = 16 + 9 + 4 + 5 = 34.
    Also S(10, 100) ≡ 845339386 (mod 1234567891).

    Find S(10^4, 10^16). Give your answer modulo 1234567891.

URL: https://projecteuler.net/problem=822
"""
from typing import Any

euler_problem: int = 822
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 5, 'm': 3}, 'answer': None},
    {'category': 'main', 'input': {'n': 10000, 'm': 10000000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'n': 10, 'm': 100}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

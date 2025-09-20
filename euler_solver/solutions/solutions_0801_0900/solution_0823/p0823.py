#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 823: Factor Shuffle.

Problem Statement:
    A list initially contains the numbers 2, 3, ..., n.
    At each round, every number in the list is divided by its smallest prime factor.
    Then the product of these smallest prime factors is added to the list as a new number.
    Finally, all numbers that become 1 are removed from the list.

    For example, below are the first three rounds for n = 5:
    [2, 3, 4, 5] -> (1) -> [2, 60] -> (2) -> [30, 4] -> (3) -> [15, 2, 4].
    Let S(n, m) be the sum of all numbers in the list after m rounds.
    For example, S(5, 3) = 15 + 2 + 4 = 21.
    Also S(10, 100) = 257.

    Find S(10^4, 10^16). Give your answer modulo 1234567891.

URL: https://projecteuler.net/problem=823
"""
from typing import Any

euler_problem: int = 823
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 5, 'm': 3}, 'answer': None},
    {'category': 'main', 'input': {'n': 10000, 'm': 10000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    '/BWEFSvqf2M='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

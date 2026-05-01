#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 187: Semiprimes.

Problem Statement:
    A composite is a number containing at least two prime factors. For example,
    15 = 3 * 5; 9 = 3 * 3; 12 = 2 * 2 * 3.

    There are ten composites below thirty containing precisely two, not
    necessarily distinct, prime factors: 4, 6, 9, 10, 14, 15, 21, 22, 25, 26.

    How many composite integers, n < 10^8, have precisely two, not necessarily
    distinct, prime factors?

URL: https://projecteuler.net/problem=187
"""
from typing import Any

euler_problem: int = 187
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 30}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

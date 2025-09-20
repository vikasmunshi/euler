#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 134: Prime Pair Connection.

Problem Statement:
    Consider the consecutive primes p1 = 19 and p2 = 23. It can be verified that
    1219 is the smallest number such that the last digits are formed by p1 whilst
    also being divisible by p2.

    In fact, with the exception of p1 = 3 and p2 = 5, for every pair of consecutive
    primes, p2 > p1, there exist values of n for which the last digits are formed
    by p1 and n is divisible by p2. Let S be the smallest of these values of n.

    Find the sum of S for every pair of consecutive primes with 5 <= p1 <= 1000000.

URL: https://projecteuler.net/problem=134
"""
from typing import Any

euler_problem: int = 134
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 2000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'TUnCQGn6QCk='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

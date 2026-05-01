#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 266: Pseudo Square Root.

Problem Statement:
    The divisors of 12 are: 1, 2, 3, 4, 6 and 12.
    The largest divisor of 12 that does not exceed the square root of 12 is 3.
    We shall call the largest divisor of an integer n that does not exceed the
    square root of n the pseudo square root (PSR) of n.
    It can be seen that PSR(3102) = 47.

    Let p be the product of the primes below 190.
    Find PSR(p) mod 10^16.

URL: https://projecteuler.net/problem=266
"""
from typing import Any

euler_problem: int = 266
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 190}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 268: At Least Four Distinct Prime Factors Less Than 100.

Problem Statement:
    It can be verified that there are 23 positive integers less than 1000 that
    are divisible by at least four distinct primes less than 100.

    Find how many positive integers less than 10^16 are divisible by at least
    four distinct primes less than 100.

URL: https://projecteuler.net/problem=268
"""
from typing import Any

euler_problem: int = 268
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 100000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

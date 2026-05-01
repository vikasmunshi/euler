#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 291: Panaitopol Primes.

Problem Statement:
    A prime number p is called a Panaitopol prime if p = (x^4 - y^4)/(x^3 + y^3)
    for some positive integers x and y.
    Find how many Panaitopol primes are less than 5*10^15.

URL: https://projecteuler.net/problem=291
"""
from typing import Any

euler_problem: int = 291
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 5000000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 50000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'qQIkBAG9MGeH1tYQ'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

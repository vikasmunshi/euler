#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 204: Generalised Hamming Numbers.

Problem Statement:
    A Hamming number is a positive number which has no prime factor larger than 5.
    So the first few Hamming numbers are 1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 15.
    There are 1105 Hamming numbers not exceeding 10^8.

    We will call a positive number a generalised Hamming number of type n, if it
    has no prime factor larger than n.
    Hence the Hamming numbers are the generalised Hamming numbers of type 5.

    How many generalised Hamming numbers of type 100 are there which don't exceed
    10^9?

URL: https://projecteuler.net/problem=204
"""
from typing import Any

euler_problem: int = 204
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 5, 'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'n': 100, 'max_limit': 1000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'c18Mhg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 248: Euler's Totient Function Equals 13!.

Problem Statement:
    The first number n for which phi(n) = 13! is 6227180929.
    Find the 150000th such number.

URL: https://projecteuler.net/problem=248
"""
from typing import Any

euler_problem: int = 248
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 1}, 'answer': None},
    {'category': 'main', 'input': {'n': 150000}, 'answer': None},
    {'category': 'extra', 'input': {'n': 10000}, 'answer': None},
]
encrypted: str = (
    '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'
    'bqZZ9Q=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

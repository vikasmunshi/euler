#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 303: Multiples with Small Digits.

Problem Statement:
    For a positive integer n, define f(n) as the least positive multiple of n
    that, written in base 10, uses only digits <= 2.

    Thus f(2) = 2, f(3) = 12, f(7) = 21, f(42) = 210, f(89) = 1121222.

    Also, sum_{n = 1}^{100} f(n)/n = 11363107.

    Find sum_{n = 1}^{10000} f(n)/n.

URL: https://projecteuler.net/problem=303
"""
from typing import Any

euler_problem: int = 303
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 20000}, 'answer': None},
]
encrypted: str = (
    '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'
    'O2Ddtuu2ngpLTeqrJbK7pNX+Dyc='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

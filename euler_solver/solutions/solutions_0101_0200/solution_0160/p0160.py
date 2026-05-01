#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 160: Factorial Trailing Digits.

Problem Statement:
    For any N, let f(N) be the last five digits before the trailing zeroes in N!.
    For example,
    9! = 362880 so f(9)=36288
    10! = 3628800 so f(10)=36288
    20! = 2432902008176640000 so f(20)=17664

    Find f(1000000000000).

URL: https://projecteuler.net/problem=160
"""
from typing import Any

euler_problem: int = 160
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

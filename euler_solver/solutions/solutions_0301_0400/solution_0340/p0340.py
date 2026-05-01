#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 340: Crazy Function.

Problem Statement:
    For fixed integers a, b, c, define the crazy function F(n) as follows:
    F(n) = n - c for all n > b
    F(n) = F(a + F(a + F(a + F(a + n)))) for all n <= b

    Also, define S(a, b, c) = sum_{n = 0}^b F(n).

    For example, if a = 50, b = 2000 and c = 40, then F(0) = 3240 and F(2000)
    = 2040. Also, S(50, 2000, 40) = 5204240.

    Find the last 9 digits of S(21^7, 7^21, 12^7).

URL: https://projecteuler.net/problem=340
"""
from typing import Any

euler_problem: int = 340
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'a': 50, 'b': 2000, 'c': 40}, 'answer': None},
    {'category': 'main', 'input': {'a': 1801088541, 'b': 558545864083284007, 'c': 35831808}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

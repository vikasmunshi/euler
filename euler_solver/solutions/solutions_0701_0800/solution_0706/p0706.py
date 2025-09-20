#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 706: 3-Like Numbers.

Problem Statement:
    For a positive integer n, define f(n) to be the number of non-empty substrings
    of n that are divisible by 3. For example, the string "2573" has 10 non-empty
    substrings, three of which represent numbers that are divisible by 3, namely
    57, 573 and 3. So f(2573) = 3.

    If f(n) is divisible by 3 then we say that n is 3-like.

    Define F(d) to be how many d digit numbers are 3-like. For example, F(2) = 30
    and F(6) = 290898.

    Find F(10^5). Give your answer modulo 1,000,000,007.

URL: https://projecteuler.net/problem=706
"""
from typing import Any

euler_problem: int = 706
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'d': 2}, 'answer': None},
    {'category': 'main', 'input': {'d': 100000}, 'answer': None},
    {'category': 'extra', 'input': {'d': 1000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'TM0QyQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

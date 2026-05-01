#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 735: Divisors of 2n^2.

Problem Statement:
    Let f(n) be the number of divisors of 2n^2 that are no greater than n.
    For example, f(15)=8 because there are 8 such divisors:
    1, 2, 3, 5, 6, 9, 10, 15.
    Note that 18 is also a divisor of 2×15^2 but it is not counted because it
    is greater than 15.

    Let F(N) = sum_{n=1}^N f(n). You are given F(15)=63, and F(1000)=15066.

    Find F(10^12).

URL: https://projecteuler.net/problem=735
"""
from typing import Any

euler_problem: int = 735
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 15}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    '1ghekgkYLpNNr3StE5gjpq2rOiA='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

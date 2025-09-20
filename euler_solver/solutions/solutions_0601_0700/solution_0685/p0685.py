#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 685: Inverse Digit Sum II.

Problem Statement:
    Writing down the numbers which have a digit sum of 10 in ascending order, we get:
    19, 28, 37, 46, 55, 64, 73, 82, 91, 109, 118, ...

    Let f(n,m) be the m-th occurrence of the digit sum n. For example, f(10,1)=19, f(10,10)=109
    and f(10,100)=1423.

    Let S(k) = sum from n=1 to k of f(n^3, n^4). For example, S(3) = 7128 and S(10) is congruent
    to 32287064 modulo 1,000,000,007.

    Find S(10,000) modulo 1,000,000,007.

URL: https://projecteuler.net/problem=685
"""
from typing import Any

euler_problem: int = 685
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'k': 3}, 'answer': None},
    {'category': 'main', 'input': {'k': 10000}, 'answer': None},
]
encrypted: str = (
    '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'
    'ii7oPq12jfo='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

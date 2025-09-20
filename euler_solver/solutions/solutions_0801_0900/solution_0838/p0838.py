#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 838: Not Coprime.

Problem Statement:
    Let f(N) be the smallest positive integer that is not coprime to any positive integer
    n ≤ N whose least significant digit is 3.

    For example f(40) equals to 897 = 3 · 13 · 23 since it is not coprime to any of 3, 13,
    23, 33. By taking the natural logarithm (log to base e) we obtain ln f(40) = ln 897
    ≈ 6.799056 when rounded to six digits after the decimal point.

    You are also given ln f(2800) ≈ 715.019337.

    Find f(10^6). Enter its natural logarithm rounded to six digits after the decimal point.

URL: https://projecteuler.net/problem=838
"""
from typing import Any

euler_problem: int = 838
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 40}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'g6UvHngRPJae9ovKQtXzfhMzNjA='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

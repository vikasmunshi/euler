#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 294: Sum of Digits - Experience #23.

Problem Statement:
    For a positive integer k, define d(k) as the sum of the digits of k
    in its usual decimal representation. Thus d(42) = 4+2 = 6.

    For a positive integer n, define S(n) as the number of positive integers
    k < 10^n with the following properties:
    - k is divisible by 23
    - d(k) = 23

    You are given that S(9) = 263626 and S(42) = 6377168878570056.

    Find S(11^12) and give your answer mod 10^9.

URL: https://projecteuler.net/problem=294
"""
from typing import Any

euler_problem: int = 294
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 9}, 'answer': None},
    {'category': 'main', 'input': {'n': 3138428376721}, 'answer': None},
    {'category': 'extra', 'input': {'n': 42}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

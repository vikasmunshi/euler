#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 817: Digits in Squares.

Problem Statement:
    Define m = M(n, d) to be the smallest positive integer such that when m^2 is written
    in base n it includes the base n digit d. For example, M(10,7) = 24 because if all the
    squares are written out in base 10 the first time the digit 7 occurs is in 24^2 = 576.
    M(11,10) = 19 as 19^2 = 361 = 2A9_11.

    Find the sum from d = 1 to 10^5 of M(p, p - d) where p = 10^9 + 7.

URL: https://projecteuler.net/problem=817
"""
from typing import Any

euler_problem: int = 817
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    '8Ml0oedRB870fo36oQZ7Vw/Ad5YmfrbmSWTwDA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

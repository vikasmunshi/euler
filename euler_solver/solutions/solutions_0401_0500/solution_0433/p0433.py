#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 433: Steps in Euclid's Algorithm.

Problem Statement:
    Let E(x_0, y_0) be the number of steps it takes to determine the greatest
    common divisor of x_0 and y_0 with Euclid's algorithm. More formally:
    x_1 = y_0, y_1 = x_0 mod y_0
    x_n = y_{n-1}, y_n = x_{n-1} mod y_{n-1}
    E(x_0, y_0) is the smallest n such that y_n = 0.

    We have E(1,1) = 1, E(10,6) = 3 and E(6,10) = 4.

    Define S(N) as the sum of E(x,y) for 1 ≤ x,y ≤ N.
    We have S(1) = 1, S(10) = 221 and S(100) = 39826.

    Find S(5·10^6).

URL: https://projecteuler.net/problem=433
"""
from typing import Any

euler_problem: int = 433
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 5000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

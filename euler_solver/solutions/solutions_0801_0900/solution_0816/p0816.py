#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 816: Shortest Distance Among Points.

Problem Statement:
    We create an array of points  P_n in a two dimensional plane using the following
    random number generator:
        s_0=290797
        s_{n+1} = (s_n)^2 mod 50515093

    P_n = (s_{2n}, s_{2n+1})

    Let d(k) be the shortest distance of any two (distinct) points among P_0, ...,
    P_{k - 1}.
    For example, d(14) = 546446.466846479.

    Find d(2000000). Give your answer rounded to 9 places after the decimal point.

URL: https://projecteuler.net/problem=816
"""
from typing import Any

euler_problem: int = 816
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'k': 14}, 'answer': None},
    {'category': 'main', 'input': {'k': 2000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

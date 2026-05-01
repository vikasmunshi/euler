#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 440: GCD and Tiling.

Problem Statement:
    We want to tile a board of length n and height 1 completely, with either 1 x 2
    blocks or 1 x 1 blocks with a single decimal digit on top.

    For example, here are some of the ways to tile a board of length n = 8.

    Let T(n) be the number of ways to tile a board of length n as described above.

    For example, T(1) = 10 and T(2) = 101.

    Let S(L) be the triple sum sum_{a, b, c} gcd(T(c^a), T(c^b)) for 1 <= a, b, c <= L.

    For example:
    S(2) = 10444
    S(3) = 1292115238446807016106539989
    S(4) mod 987898789 = 670616280.

    Find S(2000) mod 987898789.

URL: https://projecteuler.net/problem=440
"""
from typing import Any

euler_problem: int = 440
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 2}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 2000}, 'answer': None},
]
encrypted: str = (
    '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'
    'cQ2ytf2cax7jkAgvclCm62aqCDY='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

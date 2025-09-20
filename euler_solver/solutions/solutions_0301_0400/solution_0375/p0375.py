#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 375: Minimum of Subsequences.

Problem Statement:
    Let S_n be an integer sequence produced with the following pseudo-random
    number generator:
        S_0 = 290797
        S_{n+1} = S_n^2 mod 50515093

    Let A(i, j) be the minimum of the numbers S_i, S_{i+1}, ..., S_j for
    i ≤ j.
    Let M(N) = sum A(i, j) for 1 ≤ i ≤ j ≤ N.
    We can verify that M(10) = 432256955 and M(10000) = 3264567774119.

    Find M(2000000000).

URL: https://projecteuler.net/problem=375
"""
from typing import Any

euler_problem: int = 375
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 10}, 'answer': None},
    {'category': 'main', 'input': {'n': 2000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

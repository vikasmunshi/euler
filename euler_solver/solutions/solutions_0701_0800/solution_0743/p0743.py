#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 743: Window into a Matrix.

Problem Statement:
    A window into a matrix is a contiguous sub matrix.

    Consider a 2 x n matrix where every entry is either 0 or 1.
    Let A(k,n) be the total number of these matrices such that the sum of the entries in
    every 2 x k window is k.

    You are given that A(3,9) = 560 and A(4,20) = 1060870.

    Find A(10^8,10^16). Give your answer modulo 1000000007.

URL: https://projecteuler.net/problem=743
"""
from typing import Any

euler_problem: int = 743
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'k': 3, 'n': 9}, 'answer': None},
    {'category': 'main', 'input': {'k': 100000000, 'n': 10000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    't9YAKEq3+umlux4pPzYLKg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

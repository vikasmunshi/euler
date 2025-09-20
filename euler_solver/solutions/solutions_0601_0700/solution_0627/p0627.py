#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 627: Counting Products.

Problem Statement:
    Consider the set S of all possible products of n positive integers not exceeding m,
    that is
    S = { x_1 x_2 ... x_n | 1 <= x_1, x_2, ..., x_n <= m }.

    Let F(m, n) be the number of distinct elements of the set S.
    For example, F(9, 2) = 36 and F(30, 2) = 308.

    Find F(30, 10001) mod 1000000007.

URL: https://projecteuler.net/problem=627
"""
from typing import Any

euler_problem: int = 627
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'m': 9, 'n': 2}, 'answer': None},
    {'category': 'main', 'input': {'m': 30, 'n': 10001}, 'answer': None},
]
encrypted: str = (
    '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'
    'zADdPeo+Rt70Vtnd'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

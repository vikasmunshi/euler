#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 495: Writing n as the Product of k Distinct Positive Integers.

Problem Statement:
    Let W(n,k) be the number of ways in which n can be written as the product of
    k distinct positive integers.

    For example, W(144,4) = 7. There are 7 ways in which 144 can be written as a
    product of 4 distinct positive integers:
        144 = 1 x 2 x 4 x 18
        144 = 1 x 2 x 8 x 9
        144 = 1 x 2 x 3 x 24
        144 = 1 x 2 x 6 x 12
        144 = 1 x 3 x 4 x 12
        144 = 1 x 3 x 6 x 8
        144 = 2 x 3 x 4 x 6

    Note that permutations of the integers themselves are not considered distinct.

    Furthermore, W(100!,10) modulo 1000000007 = 287549200.

    Find W(10000!,30) modulo 1000000007.

URL: https://projecteuler.net/problem=495
"""
from typing import Any

euler_problem: int = 495
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n_factorial': 144, 'k': 4}, 'answer': None},
    {'category': 'main', 'input': {'n_factorial': 10000, 'k': 30}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

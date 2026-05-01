#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 793: Median of Products.

Problem Statement:
    Let S_i be an integer sequence produced with the following pseudo-random number
    generator:

        S_0 = 290797
        S_{i+1} = S_i ^ 2 mod 50515093

    Let M(n) be the median of the pairwise products S_i S_j for 0 ≤ i < j < n.

    You are given M(3) = 3878983057768 and M(103) = 492700616748525.

    Find M(1,000,003).

URL: https://projecteuler.net/problem=793
"""
from typing import Any

euler_problem: int = 793
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3}, 'answer': None},
    {'category': 'main', 'input': {'n': 1000003}, 'answer': None},
    {'category': 'extra', 'input': {'n': 10000030}, 'answer': None},
]
encrypted: str = (
    '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'
    '1rpNJtdTLla5bQPm5vW8hWNppfU='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

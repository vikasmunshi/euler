#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 912: Where are the Odds?.

Problem Statement:
    Let s_n be the n-th positive integer that does not contain three consecutive
    ones in its binary representation.
    For example, s_1 = 1 and s_7 = 8.

    Define F(N) to be the sum of n^2 for all n ≤ N where s_n is odd. You are given
    F(10) = 199.

    Find F(10^16) giving your answer modulo 10^9+7.

URL: https://projecteuler.net/problem=912
"""
from typing import Any

euler_problem: int = 912
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

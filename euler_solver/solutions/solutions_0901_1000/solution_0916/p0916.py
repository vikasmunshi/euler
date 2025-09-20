#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 916: Restricted Permutations.

Problem Statement:
    Let P(n) be the number of permutations of {1, 2, 3, ..., 2n} such that:
    1. There is no ascending subsequence with more than n+1 elements, and
    2. There is no descending subsequence with more than two elements.

    Note that subsequences need not be contiguous. For example, the permutation (4,1,
    3,2) is not counted because it has a descending subsequence of three elements: (4,3,
    2). You are given P(2) = 13 and P(10) ≡ 45265702 modulo 10^9 + 7.

    Find P(10^8) and give your answer modulo 10^9 + 7.

URL: https://projecteuler.net/problem=916
"""
from typing import Any

euler_problem: int = 916
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 2}, 'answer': None},
    {'category': 'main', 'input': {'n': 100000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'B8J1QA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

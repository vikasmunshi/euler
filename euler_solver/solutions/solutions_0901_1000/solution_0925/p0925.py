#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 925: Larger Digit Permutation III.

Problem Statement:
    Let B(n) be the smallest number larger than n that can be formed by rearranging digits
    of n, or 0 if no such number exists. For example, B(245) = 254 and B(542) = 0.

    Define T(N) = sum from n=1 to N of B(n^2). You are given T(10)=270 and T(100)=335316.

    Find T(10^16). Give your answer modulo 10^9 + 7.

URL: https://projecteuler.net/problem=925
"""
from typing import Any

euler_problem: int = 925
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'XqZYL1l9a+6kJUzcvVWNuQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

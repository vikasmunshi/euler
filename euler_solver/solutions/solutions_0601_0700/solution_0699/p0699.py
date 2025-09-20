#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 699: Triffle Numbers.

Problem Statement:
    Let sigma(n) be the sum of all the divisors of the positive integer n, for example:
    sigma(10) = 1+2+5+10 = 18.

    Define T(N) to be the sum of all numbers n ≤ N such that when the fraction sigma(n)/n is
    written in its lowest form a/b, the denominator is a power of 3 i.e. b = 3^k, k > 0.

    You are given T(100) = 270 and T(10^6) = 26089287.

    Find T(10^14).

URL: https://projecteuler.net/problem=699
"""
from typing import Any

euler_problem: int = 699
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

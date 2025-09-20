#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 365: A Huge Binomial Coefficient.

Problem Statement:
    The binomial coefficient C(10^18, 10^9) is a number with more than 9
    billion (9 x 10^9) digits.

    Let M(n, k, m) denote the binomial coefficient C(n, k) modulo m.

    Calculate sum M(10^18, 10^9, p*q*r) for 1000 < p < q < r < 5000
    and p, q, r prime.

URL: https://projecteuler.net/problem=365
"""
from typing import Any

euler_problem: int = 365
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'min_prime': 2, 'max_prime': 20}, 'answer': None},
    {'category': 'main', 'input': {'min_prime': 1000, 'max_prime': 5000}, 'answer': None},
    {'category': 'extra', 'input': {'min_prime': 1000, 'max_prime': 10000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

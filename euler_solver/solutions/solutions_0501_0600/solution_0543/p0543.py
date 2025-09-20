#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 543: Prime-Sum Numbers.

Problem Statement:
    Define function P(n, k) = 1 if n can be written as the sum of k prime numbers
    (with repetitions allowed), and P(n, k) = 0 otherwise.

    For example, P(10,2) = 1 because 10 can be written as either 3 + 7 or 5 + 5,
    but P(11,2) = 0 because no two primes can sum to 11.

    Let S(n) be the sum of all P(i,k) over 1 ≤ i,k ≤ n.

    For example, S(10) = 20, S(100) = 2402, and S(1000) = 248838.

    Let F(k) be the kth Fibonacci number (with F(0) = 0 and F(1) = 1).

    Find the sum of all S(F(k)) over 3 ≤ k ≤ 44.

URL: https://projecteuler.net/problem=543
"""
from typing import Any

euler_problem: int = 543
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000}, 'answer': None},
]
encrypted: str = (
    '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'
    '1eHCu9zVVJdrU1Fq'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

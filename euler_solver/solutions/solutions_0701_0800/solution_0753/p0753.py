#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 753: Fermat Equation.

Problem Statement:
    Fermat's Last Theorem states that no three positive integers a, b, c satisfy the
    equation a^n + b^n = c^n for any integer value of n greater than 2.

    For this problem we are only considering the case n=3. For certain values of p, it
    is possible to solve the congruence equation:
    a^3 + b^3 ≡ c^3 (mod p)

    For a prime p, we define F(p) as the number of integer solutions to this equation
    for 1 ≤ a, b, c < p.

    You are given F(5) = 12 and F(7) = 0.

    Find the sum of F(p) over all primes p less than 6,000,000.

URL: https://projecteuler.net/problem=753
"""
from typing import Any

euler_problem: int = 753
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 6000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

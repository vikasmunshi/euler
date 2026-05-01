#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 530: GCD of Divisors.

Problem Statement:
    Every divisor d of a number n has a complementary divisor n/d.

    Let f(n) be the sum of the greatest common divisor of d and n/d over all
    positive divisors d of n, that is f(n) = sum over d|n of gcd(d, n/d).

    Let F be the summatory function of f, that is F(k) = sum from n=1 to k of f(n).

    You are given that F(10) = 32 and F(1000) = 12776.

    Find F(10^15).

URL: https://projecteuler.net/problem=530
"""
from typing import Any

euler_problem: int = 530
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

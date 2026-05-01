#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 457: A Polynomial Modulo the Square of a Prime.

Problem Statement:
    Let f(n) = n^2 - 3n - 1.
    Let p be a prime.
    Let R(p) be the smallest positive integer n such that f(n) mod p^2 = 0 if such an integer n exists,
    otherwise R(p) = 0.

    Let SR(L) be the sum of R(p) for all primes not exceeding L.

    Find SR(10^7).

URL: https://projecteuler.net/problem=457
"""
from typing import Any

euler_problem: int = 457
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'limit': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 130: Composites with Prime Repunit Property.

Problem Statement:
    A number consisting entirely of ones is called a repunit. We shall define R(k)
    to be a repunit of length k; for example, R(6) = 111111.

    Given that n is a positive integer and gcd(n, 10) = 1, it can be shown that
    there always exists a value, k, for which R(k) is divisible by n, and let
    A(n) be the least such value of k; for example, A(7) = 6 and A(41) = 5.

    You are given that for all primes p > 5 that p - 1 is divisible by A(p).
    For example, when p = 41, A(41) = 5, and 40 is divisible by 5.

    However, there are rare composite values for which this is also true; the
    first five examples being 91, 259, 451, 481, and 703.

    Find the sum of the first twenty-five composite values of n for which
    gcd(n, 10) = 1 and n - 1 is divisible by A(n).

URL: https://projecteuler.net/problem=130
"""
from typing import Any

euler_problem: int = 130
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'count': 5}, 'answer': None},
    {'category': 'main', 'input': {'count': 25}, 'answer': None},
    {'category': 'extra', 'input': {'count': 100}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

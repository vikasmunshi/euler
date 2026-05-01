#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 487: Sums of Power Sums.

Problem Statement:
    Let f_k(n) be the sum of the k-th powers of the first n positive integers.

    For example, f_2(10) = 1^2 + 2^2 + 3^2 + 4^2 + 5^2 + 6^2 + 7^2 + 8^2 + 9^2 + 10^2 = 385.

    Let S_k(n) be the sum of f_k(i) for 1 ≤ i ≤ n. For example, S_4(100) = 35375333830.

    What is the sum of (S_10000(10^12) modulo p) over all primes p between 2 * 10^9 and
    2 * 10^9 + 2000?

URL: https://projecteuler.net/problem=487
"""
from typing import Any

euler_problem: int = 487
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'ZXRbmZJTfqowRhIF7TORJQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

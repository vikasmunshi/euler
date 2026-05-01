#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 643: 2-Friendly.

Problem Statement:
    Two positive integers a and b are 2-friendly when gcd(a,b) = 2^t, t > 0.
    For example, 24 and 40 are 2-friendly because gcd(24,40) = 8 = 2^3 while
    24 and 36 are not because gcd(24,36) = 12 = 2^2 * 3 not a power of 2.

    Let f(n) be the number of pairs, (p,q), of positive integers with
    1 <= p < q <= n such that p and q are 2-friendly. You are given
    f(10^2) = 1031 and f(10^6) = 321418433 modulo 1,000,000,007.

    Find f(10^11) modulo 1,000,000,007.

URL: https://projecteuler.net/problem=643
"""
from typing import Any

euler_problem: int = 643
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'JZYB1sk39R/Ms7Uy4HrejA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

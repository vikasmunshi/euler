#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 635: Subset Sums.

Problem Statement:
    Let A_q(n) be the number of subsets, B, of the set {1, 2, ..., q*n} that satisfy two
    conditions:
    1) B has exactly n elements;
    2) the sum of the elements of B is divisible by n.

    For example, A_2(5) = 52 and A_3(5) = 603.

    Let S_q(L) = sum of A_q(p) over all primes p ≤ L.
    For example, S_2(10) = 554, S_2(100) mod 1,000,000,009 = 100433628, and
    S_3(100) mod 1,000,000,009 = 855618282.

    Find S_2(10^8) + S_3(10^8) modulo 1,000,000,009.

URL: https://projecteuler.net/problem=635
"""
from typing import Any

euler_problem: int = 635
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

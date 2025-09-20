#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 565: Divisibility of Sum of Divisors.

Problem Statement:
    Let σ(n) be the sum of the divisors of n.
    E.g. the divisors of 4 are 1, 2 and 4, so σ(4) = 7.

    The numbers n not exceeding 20 such that 7 divides σ(n) are: 4, 12, 13 and 20,
    the sum of these numbers being 49.

    Let S(n, d) be the sum of the numbers i not exceeding n such that d divides σ(i).
    So S(20, 7) = 49.

    You are given: S(10^6, 2017) = 150850429 and S(10^9, 2017) = 249652238344557.

    Find S(10^11, 2017).

URL: https://projecteuler.net/problem=565
"""
from typing import Any

euler_problem: int = 565
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 20, 'divisor': 7}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000000, 'divisor': 2017}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 934: Unlucky Primes.

Problem Statement:
    We define the unlucky prime of a number n, denoted u(n), as the smallest prime
    number p such that the remainder of n divided by p (i.e. n mod p) is not a
    multiple of seven.

    For example, u(14) = 3, u(147) = 2 and u(1470) = 13.

    Let U(N) be the sum of u(n) for n = 1 to N.

    You are given U(1470) = 4293.

    Find U(10^17).

URL: https://projecteuler.net/problem=934
"""
from typing import Any

euler_problem: int = 934
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'AUXuRE6fezDHmRUoX54rp9QdNC8='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 686: Powers of Two.

Problem Statement:
    2^7=128 is the first power of two whose leading digits are "12".
    The next power of two whose leading digits are "12" is 2^80.

    Define p(L, n) to be the n-th smallest value of j such that the base 10
    representation of 2^j begins with the digits of L.
    So p(12, 1) = 7 and p(12, 2) = 80.

    You are also given that p(123, 45) = 12710.

    Find p(123, 678910).

URL: https://projecteuler.net/problem=686
"""
from typing import Any

euler_problem: int = 686
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'L': 12, 'n': 2}, 'answer': None},
    {'category': 'main', 'input': {'L': 123, 'n': 678910}, 'answer': None},
    {'category': 'extra', 'input': {'L': 1234, 'n': 1000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'bBnZxKimO5Z4k1pEtFiihAL+W1Og38dYWKfTYg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 200: Prime-proof Squbes.

Problem Statement:
    We shall define a sqube to be a number of the form, p^2 q^3, where p and q are
    distinct primes. For example, 200 = 5^2 2^3 or 120072949 = 23^2 61^3.

    The first five squbes are 72, 108, 200, 392, and 500.

    Interestingly, 200 is also the first number for which you cannot change any single
    digit to make a prime; we shall call such numbers, prime-proof. The next
    prime-proof sqube which contains the contiguous sub-string "200" is 1992008.

    Find the 200th prime-proof sqube containing the contiguous sub-string "200".

URL: https://projecteuler.net/problem=200
"""
from typing import Any

euler_problem: int = 200
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 1}, 'answer': None},
    {'category': 'main', 'input': {'n': 200}, 'answer': None},
]
encrypted: str = (
    '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'
    'VqTrtuBIfMklKtf3Tod3HzdhE/k='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

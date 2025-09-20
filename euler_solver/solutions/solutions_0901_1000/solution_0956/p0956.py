#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 956: Super Duper Sum.

Problem Statement:
    The total number of prime factors of n, counted with multiplicity, is denoted Omega(n).
    For example, Omega(12)=3, counting the factor 2 twice, and the factor 3 once.

    Define D(n, m) to be the sum of all divisors d of n where Omega(d) is divisible by m.
    For example, D(24, 3)=1+8+12=21.

    The superfactorial of n, often written as n$, is defined as the product of the first n factorials:
    n$ = 1! x 2! x ... x n!

    The superduperfactorial of n, we write as n*, is defined as the product of the first n superfactorials:
    n* = 1$ x 2$ x ... x n$

    You are given D(6*, 6)=6368195719791280.

    Find D(1000*, 1000).
    Give your answer modulo 999999001.

URL: https://projecteuler.net/problem=956
"""
from typing import Any

euler_problem: int = 956
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 6, 'm': 6}, 'answer': None},
    {'category': 'main', 'input': {'n': 1000, 'm': 1000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

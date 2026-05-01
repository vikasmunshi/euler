#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 708: Twos Are All You Need.

Problem Statement:
    A positive integer, n, is factorised into prime factors. We define f(n) to be
    the product when each prime factor is replaced with 2. In addition we define
    f(1)=1.

    For example, 90 = 2 x 3 x 3 x 5, then replacing the primes, 2 x 2 x 2 x 2 = 16,
    hence f(90) = 16.

    Let S(N) = sum_{n=1}^N f(n). You are given S(10^8) = 9613563919.

    Find S(10^14).

URL: https://projecteuler.net/problem=708
"""
from typing import Any

euler_problem: int = 708
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

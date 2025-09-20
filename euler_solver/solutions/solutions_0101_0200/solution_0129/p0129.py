#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 129: Repunit Divisibility.

Problem Statement:
    A number consisting entirely of ones is called a repunit. We shall define
    R(k) to be a repunit of length k; for example, R(6) = 111111.
    Given that n is a positive integer and gcd(n, 10) = 1, it can be shown
    that there always exists a value k for which R(k) is divisible by n, and
    let A(n) be the least such value of k; for example, A(7) = 6 and A(41) = 5.
    The least value of n for which A(n) first exceeds ten is 17.
    Find the least value of n for which A(n) first exceeds one-million.

URL: https://projecteuler.net/problem=129
"""
from typing import Any

euler_problem: int = 129
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 2000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'rIpXXUiixeDnPBgfuzo1FLBXK8i9yaluQpcSwg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

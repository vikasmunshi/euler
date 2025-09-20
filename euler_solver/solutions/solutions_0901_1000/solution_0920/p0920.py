#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 920: Tau Numbers.

Problem Statement:
    For a positive integer n we define tau(n) to be the count of the divisors of n.
    For example, the divisors of 12 are {1,2,3,4,6,12} and so tau(12) = 6.

    A positive integer n is a tau number if it is divisible by tau(n). For example tau(12)=6
    and 6 divides 12 so 12 is a tau number.

    Let m(k) be the smallest tau number x such that tau(x) = k. For example, m(8) = 24,
    m(12) = 60 and m(16) = 384.

    Further define M(n) to be the sum of all m(k) whose values do not exceed 10^n. You are
    given M(3) = 3189.

    Find M(16).

URL: https://projecteuler.net/problem=920
"""
from typing import Any

euler_problem: int = 920
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3}, 'answer': None},
    {'category': 'main', 'input': {'n': 16}, 'answer': None},
]
encrypted: str = (
    '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'
    'hKgOQa8pXoFMJKIE'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

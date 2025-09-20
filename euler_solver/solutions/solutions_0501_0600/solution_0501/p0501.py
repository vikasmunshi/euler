#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 501: Eight Divisors.

Problem Statement:
    The eight divisors of 24 are 1, 2, 3, 4, 6, 8, 12 and 24.
    The ten numbers not exceeding 100 having exactly eight divisors are
    24, 30, 40, 42, 54, 56, 66, 70, 78 and 88.
    Let f(n) be the count of numbers not exceeding n with exactly eight
    divisors.
    You are given f(100) = 10, f(1000) = 180 and f(10^6) = 224427.
    Find f(10^12).

URL: https://projecteuler.net/problem=501
"""
from typing import Any

euler_problem: int = 501
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

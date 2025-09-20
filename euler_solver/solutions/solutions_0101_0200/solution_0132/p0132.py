#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 132: Large Repunit Factors.

Problem Statement:
    A number consisting entirely of ones is called a repunit. We shall define
    R(k) to be a repunit of length k.

    For example, R(10) = 1111111111 = 11 * 41 * 271 * 9091, and the sum of these
    prime factors is 9414.

    Find the sum of the first forty prime factors of R(10^9).

URL: https://projecteuler.net/problem=132
"""
from typing import Any

euler_problem: int = 132
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 4, 'repunit_length': 10}, 'answer': None},
    {'category': 'main', 'input': {'n': 40, 'repunit_length': 1000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'hRIFfCRnZsHrh/z6oxyVYPljCEwvanuOd70BCg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

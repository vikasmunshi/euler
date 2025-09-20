#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 258: A Lagged Fibonacci Sequence.

Problem Statement:
    A sequence is defined as:
    g_k = 1, for 0 <= k <= 1999
    g_k = g_{k-2000} + g_{k-1999}, for k >= 2000.
    Find g_k mod 20092010 for k = 10^18.

URL: https://projecteuler.net/problem=258
"""
from typing import Any

euler_problem: int = 258
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'k': 10, 'modulus': 1000}, 'answer': None},
    {'category': 'main', 'input': {'k': 1000000000000000000, 'modulus': 20092010}, 'answer': None},
    {'category': 'extra', 'input': {'k': 1000000000000, 'modulus': 20092010}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 250: $250250$.

Problem Statement:
    Find the number of non-empty subsets of {1^1, 2^2, 3^3, ..., 250250^250250},
    the sum of whose elements is divisible by 250.
    Enter the rightmost 16 digits as your answer.

URL: https://projecteuler.net/problem=250
"""
from typing import Any

euler_problem: int = 250
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10, 'digits': 16}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 250250, 'digits': 16}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 10000, 'digits': 16}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

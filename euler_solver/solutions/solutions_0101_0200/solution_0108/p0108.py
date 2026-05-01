#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 108: Diophantine Reciprocals I.

Problem Statement:
    In the following equation x, y, and n are positive integers.

        1/x + 1/y = 1/n

    For n = 4 there are exactly three distinct solutions:

        1/5 + 1/20 = 1/4
        1/6 + 1/12 = 1/4
        1/8 + 1/8  = 1/4

    What is the least value of n for which the number of distinct solutions
    exceeds one-thousand?

URL: https://projecteuler.net/problem=108
"""
from typing import Any

euler_problem: int = 108
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'min_solutions': 3}, 'answer': None},
    {'category': 'dev', 'input': {'min_solutions': 10}, 'answer': None},
    {'category': 'dev', 'input': {'min_solutions': 100}, 'answer': None},
    {'category': 'main', 'input': {'min_solutions': 1000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 918: Recursive Sequence Summation.

Problem Statement:
    The sequence a_n is defined by a_1=1, and then recursively for n≥1:
        a_2n  = 2a_n
        a_2n+1 = a_n - 3a_n+1
    The first ten terms are 1, 2, -5, 4, 17, -10, -17, 8, -47, 34.
    Define S(N) = sum from n=1 to N of a_n. You are given S(10) = -13.
    Find S(10^12).

URL: https://projecteuler.net/problem=918
"""
from typing import Any

euler_problem: int = 918
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'b3VZlNsaCqPgrduKm746Pw=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

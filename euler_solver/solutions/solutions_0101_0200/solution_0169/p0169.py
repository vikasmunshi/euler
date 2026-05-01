#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 169: Sums of Powers of Two.

Problem Statement:
    Define f(0) = 1 and f(n) to be the number of different ways n can be
    expressed as a sum of integer powers of 2 using each power no more than
    twice.

    For example, f(10) = 5 since there are five different ways to express 10:
    1 + 1 + 8
    1 + 1 + 4 + 4
    1 + 1 + 2 + 2 + 4
    2 + 4 + 4
    2 + 8

    What is f(10^25)?

URL: https://projecteuler.net/problem=169
"""
from typing import Any

euler_problem: int = 169
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 10}, 'answer': None},
    {'category': 'main', 'input': {'n': 10000000000000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'FSuPI1hIITk='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

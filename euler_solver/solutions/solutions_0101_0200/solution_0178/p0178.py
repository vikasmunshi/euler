#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 178: Step Numbers.

Problem Statement:
    Consider the number 45656.
    It can be seen that each pair of consecutive digits of 45656 has a difference of
    one.
    A number for which every pair of consecutive digits has a difference of one is
    called a step number.
    A pandigital number contains every decimal digit from 0 to 9 at least once.
    How many pandigital step numbers less than 10^40 are there?

URL: https://projecteuler.net/problem=178
"""
from typing import Any

euler_problem: int = 178
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000000000000000000000000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

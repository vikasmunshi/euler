#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 136: Singleton Difference.

Problem Statement:
    The positive integers, x, y, and z, are consecutive terms of an arithmetic
    progression. Given that n is a positive integer, the equation,
    x^2 - y^2 - z^2 = n, has exactly one solution when n = 20:
    13^2 - 10^2 - 7^2 = 20.

    In fact there are twenty-five values of n below one hundred for which the
    equation has a unique solution.

    How many values of n less than fifty million have exactly one solution?

URL: https://projecteuler.net/problem=136
"""
from typing import Any

euler_problem: int = 136
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 50000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'DMXfEA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 342: The Totient of a Square Is a Cube.

Problem Statement:
    Consider the number 50.
    50^2 = 2500 = 2^2 * 5^4, so phi(2500) = 2 * 4 * 5^3 = 8 * 5^3 = 2^3 * 5^3.
    So 2500 is a square and phi(2500) is a cube.

    Find the sum of all numbers n, 1 < n < 10^10 such that phi(n^2) is a cube.

    phi denotes Euler's totient function.

URL: https://projecteuler.net/problem=342
"""
from typing import Any

euler_problem: int = 342
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

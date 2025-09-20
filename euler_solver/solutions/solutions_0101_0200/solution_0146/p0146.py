#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 146: Investigating a Prime Pattern.

Problem Statement:
    The smallest positive integer n for which the numbers n^2 + 1, n^2 + 3,
    n^2 + 7, n^2 + 9, n^2 + 13, and n^2 + 27 are consecutive primes is 10.
    The sum of all such integers n below one-million is 1242490.

    What is the sum of all such integers n below 150 million?

URL: https://projecteuler.net/problem=146
"""
from typing import Any

euler_problem: int = 146
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 150000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 100000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

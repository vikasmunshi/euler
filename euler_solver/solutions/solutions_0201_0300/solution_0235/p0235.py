#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 235: An Arithmetic Geometric Sequence.

Problem Statement:
    Given is the arithmetic-geometric sequence u(k) = (900-3k)r^{k - 1}.
    Let s(n) = sum_{k = 1}^n u(k).

    Find the value of r for which s(5000) = -600,000,000,000.

    Give your answer rounded to 12 places behind the decimal point.

URL: https://projecteuler.net/problem=235
"""
from typing import Any

euler_problem: int = 235
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'Ze8etA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

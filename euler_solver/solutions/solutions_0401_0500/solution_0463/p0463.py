#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 463: A Weird Recurrence Relation.

Problem Statement:
    The function f is defined for all positive integers as follows:

        f(1) = 1
        f(3) = 3
        f(2n) = f(n)
        f(4n + 1) = 2f(2n + 1) - f(n)
        f(4n + 3) = 3f(2n + 1) - 2f(n)

    The function S(n) is defined as the sum of f(i) for i from 1 to n.

    S(8) = 22 and S(100) = 3604.

    Find S(3^37). Give the last 9 digits of your answer.

URL: https://projecteuler.net/problem=463
"""
from typing import Any

euler_problem: int = 463
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 8}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 450283905890997363}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

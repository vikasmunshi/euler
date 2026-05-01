#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 454: Diophantine Reciprocals III.

Problem Statement:
    In the following equation x, y, and n are positive integers.

    1/x + 1/y = 1/n

    For a limit L we define F(L) as the number of solutions which satisfy
    x < y ≤ L.

    We can verify that F(15) = 4 and F(1000) = 1069.
    Find F(10^12).

URL: https://projecteuler.net/problem=454
"""
from typing import Any

euler_problem: int = 454
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 15}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 10000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

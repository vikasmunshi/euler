#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 466: Distinct Terms in a Multiplication Table.

Problem Statement:
    Let P(m,n) be the number of distinct terms in an m times n multiplication table.

    For example, a 3 times 4 multiplication table looks like this:

        1    2    3    4
        2    4    6    8
        3    6    9   12

    There are 8 distinct terms {1,2,3,4,6,8,9,12}, therefore P(3,4) = 8.

    You are given that:
    P(64,64) = 1263,
    P(12,345) = 1998, and
    P(32,10^15) = 13826382602124302.

    Find P(64,10^16).

URL: https://projecteuler.net/problem=466
"""
from typing import Any

euler_problem: int = 466
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'m': 64, 'n': 10000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'OhbqiDmk8xCpwFf55Q0Ybg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

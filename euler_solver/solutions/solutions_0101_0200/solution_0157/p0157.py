#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 157: Base-10 Diophantine Reciprocal.

Problem Statement:
    Consider the diophantine equation 1/a + 1/b = p/10^n with a, b, p, n positive
    integers and a <= b.

    For n=1 this equation has 20 solutions that are listed below:
    1/1 + 1/1 = 20/10, 1/1 + 1/2 = 15/10, 1/1 + 1/5 = 12/10,
    1/1 + 1/10 = 11/10, 1/2 + 1/2 = 10/10
    1/2 + 1/5 = 7/10, 1/2 + 1/10 = 6/10, 1/3 + 1/6 = 5/10,
    1/3 + 1/15 = 4/10, 1/4 + 1/4 = 5/10
    1/4 + 1/20 = 3/10, 1/5 + 1/5 = 4/10, 1/5 + 1/10 = 3/10,
    1/6 + 1/30 = 2/10, 1/10 + 1/10 = 2/10
    1/11 + 1/110 = 1/10, 1/12 + 1/60 = 1/10, 1/14 + 1/35 = 1/10,
    1/15 + 1/30 = 1/10, 1/20 + 1/20 = 1/10

    How many solutions has this equation for 1 <= n <= 9?

URL: https://projecteuler.net/problem=157
"""
from typing import Any

euler_problem: int = 157
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_n': 1}, 'answer': None},
    {'category': 'main', 'input': {'max_n': 9}, 'answer': None},
    {'category': 'extra', 'input': {'max_n': 12}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

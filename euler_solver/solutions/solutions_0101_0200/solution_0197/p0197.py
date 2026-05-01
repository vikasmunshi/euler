#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 197: A Recursively Defined Sequence.

Problem Statement:
    Given is the function f(x) = floor(2^(30.403243784 - x^2)) * 10^-9 (floor is
    the floor-function). The sequence u_n is defined by u_0 = -1 and
    u_{n+1} = f(u_n).

    Find u_n + u_{n+1} for n = 10^12.
    Give your answer with 9 digits after the decimal point.

URL: https://projecteuler.net/problem=197
"""
from typing import Any

euler_problem: int = 197
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 10}, 'answer': None},
    {'category': 'main', 'input': {'n': 1000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'n': 1000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'zW+MJMQCRzTAOXTy/dOdx/GN5no='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

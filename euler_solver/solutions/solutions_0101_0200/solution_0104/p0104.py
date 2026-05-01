#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 104: Pandigital Fibonacci Ends.

Problem Statement:
    The Fibonacci sequence is defined by the recurrence relation:
        F_n = F_{n - 1} + F_{n - 2}, where F_1 = 1 and F_2 = 1.
    It turns out that F_541, which contains 113 digits, is the first Fibonacci number
    for which the last nine digits are 1-9 pandigital (contain all the digits 1 to 9,
    but not necessarily in order). And F_2749, which contains 575 digits, is the first
    Fibonacci number for which the first nine digits are 1-9 pandigital.
    Given that F_k is the first Fibonacci number for which the first nine digits AND the
    last nine digits are 1-9 pandigital, find k.

URL: https://projecteuler.net/problem=104
"""
from typing import Any

euler_problem: int = 104
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'yW2fY3xustw='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

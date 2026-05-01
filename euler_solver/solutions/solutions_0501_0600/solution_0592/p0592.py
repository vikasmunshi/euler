#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 592: Factorial Trailing Digits 2.

Problem Statement:
    For any N, let f(N) be the last twelve hexadecimal digits before the trailing
    zeroes in N!.

    For example, the hexadecimal representation of 20! is 21C3677C82B40000,
    so f(20) is the digit sequence 21C3677C82B4.

    Find f(20!). Give your answer as twelve hexadecimal digits, using uppercase
    for the digits A to F.

URL: https://projecteuler.net/problem=592
"""
from typing import Any

euler_problem: int = 592
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    '2Pglu1ljHGIHG56FgXUNZ8uGX+ow07wgoVW81Q=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

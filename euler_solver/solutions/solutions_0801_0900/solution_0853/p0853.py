#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 853: Pisano Periods 1.

Problem Statement:
    For every positive integer n the Fibonacci sequence modulo n is periodic.
    The period depends on the value of n. This period is called the Pisano period
    for n, often shortened to π(n).

    There are three values of n for which π(n) equals 18: 19, 38 and 76. The sum of
    those smaller than 50 is 57.

    Find the sum of the values of n smaller than 1 000 000 000 for which π(n) equals 120.

URL: https://projecteuler.net/problem=853
"""
from typing import Any

euler_problem: int = 853
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 50}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'Br+Nr7iSAWOnpNaQTQUX64SwoGM='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

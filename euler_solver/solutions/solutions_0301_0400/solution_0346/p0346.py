#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 346: Strong Repunits.

Problem Statement:
    The number 7 is special, because 7 is 111 written in base 2, and 11
    written in base 6 (i.e. 7_10 = 11_6 = 111_2). In other words, 7 is a
    repunit in at least two bases b > 1.

    We shall call a positive integer with this property a strong repunit.
    It can be verified that there are 8 strong repunits below 50:
    {1, 7, 13, 15, 21, 31, 40, 43}.

    Furthermore, the sum of all strong repunits below 1000 equals 15864.

    Find the sum of all strong repunits below 10^12.

URL: https://projecteuler.net/problem=346
"""
from typing import Any

euler_problem: int = 346
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 50}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'uud8dVSG+U0UoC0xgzU7QXBZ/4BYZfkHv58dFg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

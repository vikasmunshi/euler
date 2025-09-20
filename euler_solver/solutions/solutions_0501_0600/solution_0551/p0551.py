#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 551: Sum of Digits Sequence.

Problem Statement:
    Let a_0, a_1, ... be an integer sequence defined by:
        a_0 = 1;
        for n >= 1, a_n is the sum of the digits of all preceding terms.

    The sequence starts with 1, 1, 2, 4, 8, 16, 23, 28, 38, 49, ...
    You are given a_10^6 = 31054319.

    Find a_10^15.

URL: https://projecteuler.net/problem=551
"""
from typing import Any

euler_problem: int = 551
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 10}, 'answer': None},
    {'category': 'main', 'input': {'n': 1000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'bjGuh7wTr1WOS92I/dAqsQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

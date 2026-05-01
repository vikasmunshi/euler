#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 119: Digit Power Sum.

Problem Statement:
    The number 512 is interesting because it is equal to the sum of its digits
    raised to some power: 5 + 1 + 2 = 8, and 8^3 = 512. Another example of a
    number with this property is 614656 = 28^4.
    We shall define a_n to be the n-th term of this sequence and insist that a
    number must contain at least two digits to have a sum.
    You are given that a_2 = 512 and a_10 = 614656.
    Find a_30.

URL: https://projecteuler.net/problem=119
"""
from typing import Any

euler_problem: int = 119
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 2}, 'answer': None},
    {'category': 'dev', 'input': {'n': 10}, 'answer': None},
    {'category': 'main', 'input': {'n': 30}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

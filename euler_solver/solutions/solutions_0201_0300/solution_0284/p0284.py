#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 284: Steady Squares.

Problem Statement:
    The 3-digit number 376 in the decimal numbering system is an example of numbers
    with the special property that its square ends with the same digits: 376^2 =
    141376. Let's call a number with this property a steady square.

    Steady squares can also be observed in other numbering systems. In the base
    14 numbering system, the 3-digit number c37 is also a steady square: c37^2 =
    aa0c37, and the sum of its digits is c+3+7=18 in the same numbering system.
    The letters a, b, c and d are used for the 10, 11, 12 and 13 digits
    respectively, in a manner similar to the hexadecimal numbering system.

    For 1 ≤ n ≤ 9, the sum of the digits of all the n-digit steady squares in the
    base 14 numbering system is 2d8 (582 decimal). Steady squares with leading
    0's are not allowed.

    Find the sum of the digits of all the n-digit steady squares in the base 14
    numbering system for 1 ≤ n ≤ 10000 (decimal) and give your answer in the base
    14 system using lower case letters where necessary.

URL: https://projecteuler.net/problem=284
"""
from typing import Any

euler_problem: int = 284
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_n': 9}, 'answer': None},
    {'category': 'main', 'input': {'max_n': 10000}, 'answer': None},
    {'category': 'extra', 'input': {'max_n': 20000}, 'answer': None},
]
encrypted: str = (
    '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'
    'ViCdgw=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

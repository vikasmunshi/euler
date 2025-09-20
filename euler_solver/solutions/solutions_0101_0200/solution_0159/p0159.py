#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 159: Digital Root Sums of Factorisations.

Problem Statement:
    A composite number can be factored many different ways. For instance, not
    including multiplication by one, 24 can be factored in 7 distinct ways:
    24 = 2 x 2 x 2 x 3
    24 = 2 x 3 x 4
    24 = 2 x 2 x 6
    24 = 4 x 6
    24 = 3 x 8
    24 = 2 x 12
    24 = 24

    The digital root of a number in base 10 is found by adding together the
    digits of that number, and repeating until a number less than 10 is
    obtained. Thus the digital root of 467 is 8.

    We shall call a Digital Root Sum (DRS) the sum of the digital roots of the
    individual factors of our number. The chart below demonstrates all of the
    DRS values for 24:
    2 x 2 x 2 x 3    -> 9
    2 x 3 x 4        -> 9
    2 x 2 x 6        -> 10
    4 x 6            -> 10
    3 x 8            -> 11
    2 x 12           -> 5
    24               -> 6

    The maximum Digital Root Sum of 24 is 11. The function mdrs(n) gives the
    maximum Digital Root Sum of n, so mdrs(24) = 11.

    Find sum mdrs(n) for 1 < n < 1,000,000.

URL: https://projecteuler.net/problem=159
"""
from typing import Any

euler_problem: int = 159
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 2000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'niTSWLHY1Q4='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

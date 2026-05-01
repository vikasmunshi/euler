#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 225: Tribonacci Non-divisors.

Problem Statement:
    The sequence 1, 1, 1, 3, 5, 9, 17, 31, 57, 105, 193, 355, 653, 1201, ...
    is defined by T_1 = T_2 = T_3 = 1 and T_n = T_{n-1} + T_{n-2} + T_{n-3}.

    It can be shown that 27 does not divide any terms of this sequence.
    In fact, 27 is the first odd number with this property.

    Find the 124th odd number that does not divide any terms of the above
    sequence.

URL: https://projecteuler.net/problem=225
"""
from typing import Any

euler_problem: int = 225
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 1}, 'answer': None},
    {'category': 'main', 'input': {'n': 124}, 'answer': None},
    {'category': 'extra', 'input': {'n': 100}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

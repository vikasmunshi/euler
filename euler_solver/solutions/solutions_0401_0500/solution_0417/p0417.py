#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 417: Reciprocal Cycles II.

Problem Statement:
    A unit fraction contains 1 in the numerator. The decimal representation of the unit fractions
    with denominators 2 to 10 are given:

        1/2 = 0.5
        1/3 = 0.(3)
        1/4 = 0.25
        1/5 = 0.2
        1/6 = 0.1(6)
        1/7 = 0.(142857)
        1/8 = 0.125
        1/9 = 0.(1)
        1/10 = 0.1

    Where 0.1(6) means 0.166666..., and has a 1-digit recurring cycle. It can be seen that 1/7 has
    a 6-digit recurring cycle.
    Unit fractions whose denominator has no other prime factors than 2 and/or 5 are not considered
    to have a recurring cycle.
    We define the length of the recurring cycle of those unit fractions as 0.
    Let L(n) denote the length of the recurring cycle of 1/n.
    You are given that the sum of L(n) for 3 ≤ n ≤ 1,000,000 equals 55535191115.
    Find the sum of L(n) for 3 ≤ n ≤ 100,000,000.

URL: https://projecteuler.net/problem=417
"""
from typing import Any

euler_problem: int = 417
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

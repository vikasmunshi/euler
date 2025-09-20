#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 621: Expressing an Integer as the Sum of Triangular Numbers.

Problem Statement:
    Gauss famously proved that every positive integer can be expressed as the sum of
    three triangular numbers (including 0 as the lowest triangular number). In fact
    most numbers can be expressed as a sum of three triangular numbers in several ways.

    Let G(n) be the number of ways of expressing n as the sum of three triangular
    numbers, regarding different arrangements of the terms of the sum as distinct.

    For example, G(9) = 7, as 9 can be expressed as: 3+3+3, 0+3+6, 0+6+3, 3+0+6,
    3+6+0, 6+0+3, 6+3+0.
    You are given G(1000) = 78 and G(10^6) = 2106.

    Find G(17526 x 10^9).

URL: https://projecteuler.net/problem=621
"""
from typing import Any

euler_problem: int = 621
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 17526000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'l7F+4Q=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

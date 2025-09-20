#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 229: Four Representations Using Squares.

Problem Statement:
    Consider the number 3600. It is very special, because

    3600 = 48^2 + 36^2
    3600 = 20^2 + 2 * 40^2
    3600 = 30^2 + 3 * 30^2
    3600 = 45^2 + 7 * 15^2

    Similarly, we find that 88201 = 99^2 + 280^2 = 287^2 + 2 * 54^2 =
    283^2 + 3 * 52^2 = 197^2 + 7 * 84^2.

    In 1747, Euler proved which numbers are representable as a sum of two
    squares. We are interested in the numbers n which admit representations
    of all of the following four types:

    n = a1^2 + b1^2
    n = a2^2 + 2 * b2^2
    n = a3^2 + 3 * b3^2
    n = a7^2 + 7 * b7^2

    where the a_k and b_k are positive integers.

    There are 75373 such numbers that do not exceed 10^7.

    How many such numbers are there that do not exceed 2 * 10^9?

URL: https://projecteuler.net/problem=229
"""
from typing import Any

euler_problem: int = 229
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 2000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 100000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'YjGrWIpViBiLqVwHSNbY1UVCWbA='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

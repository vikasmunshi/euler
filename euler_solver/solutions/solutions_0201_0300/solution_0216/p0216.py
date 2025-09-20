#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 216: The Primality of 2n^2 - 1.

Problem Statement:
    Consider numbers t(n) of the form t(n) = 2n^2 - 1 with n > 1.
    The first such numbers are 7, 17, 31, 49, 71, 97, 127 and 161.
    It turns out that only 49 = 7 * 7 and 161 = 7 * 23 are not prime.
    For n <= 10000 there are 2202 numbers t(n) that are prime.

    How many numbers t(n) are prime for n <= 50000000?

URL: https://projecteuler.net/problem=216
"""
from typing import Any

euler_problem: int = 216
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 50000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 100000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 474: Last Digits of Divisors.

Problem Statement:
    For a positive integer n and digits d, we define F(n, d) as the number of the divisors
    of n whose last digits equal d.

    For example, F(84, 4) = 3. Among the divisors of 84 (1, 2, 3, 4, 6, 7, 12, 14, 21, 28,
    42, 84), three of them (4, 14, 84) have the last digit 4.

    We can also verify that F(12!, 12) = 11 and F(50!, 123) = 17888.

    Find F(10^6!, 65432) modulo (10^16 + 61).

URL: https://projecteuler.net/problem=474
"""
from typing import Any

euler_problem: int = 474
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n_factorial': 12, 'last_digits': 12}, 'answer': None},
    {'category': 'main', 'input': {'n_factorial': 1000000, 'last_digits': 65432}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

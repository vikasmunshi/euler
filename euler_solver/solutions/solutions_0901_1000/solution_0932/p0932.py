#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 932: 2025.

Problem Statement:
    For the year 2025
    2025 = (20 + 25)^2

    Given positive integers a and b, the concatenation ab we call a 2025-number if
    ab = (a+b)^2.
    Other examples are 3025 and 81.
    Note 9801 is not a 2025-number because the concatenation of 98 and 1 is 981.

    Let T(n) be the sum of all 2025-numbers with n digits or less. You are given T(4) = 5131.

    Find T(16).

URL: https://projecteuler.net/problem=932
"""
from typing import Any

euler_problem: int = 932
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_digits': 4}, 'answer': None},
    {'category': 'main', 'input': {'max_digits': 16}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

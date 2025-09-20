#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 413: One-child Numbers.

Problem Statement:
    We say that a d-digit positive number (no leading zeros) is a one-child number
    if exactly one of its sub-strings is divisible by d.

    For example, 5671 is a 4-digit one-child number. Among all its sub-strings 5, 6,
    7, 1, 56, 67, 71, 567, 671 and 5671, only 56 is divisible by 4.
    Similarly, 104 is a 3-digit one-child number because only 0 is divisible by 3.
    1132451 is a 7-digit one-child number because only 245 is divisible by 7.

    Let F(N) be the number of the one-child numbers less than N.
    We can verify that F(10) = 9, F(10^3) = 389 and F(10^7) = 277674.

    Find F(10^19).

URL: https://projecteuler.net/problem=413
"""
from typing import Any

euler_problem: int = 413
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

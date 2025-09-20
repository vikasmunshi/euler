#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 529: 10-substrings.

Problem Statement:
    A 10-substring of a number is a substring of its digits that sum to 10. For
    example, the 10-substrings of the number 3523014 are:
        3523014
        where the substrings summing to 10 are:
        352, 523, 5230, 23014

    A number is called 10-substring-friendly if every one of its digits belongs to
    a 10-substring. For example, 3523014 is 10-substring-friendly, but 28546 is not.

    Let T(n) be the number of 10-substring-friendly numbers from 1 to 10^n (inclusive).
    For example T(2) = 9 and T(5) = 3492.

    Find T(10^18) mod 1,000,000,007.

URL: https://projecteuler.net/problem=529
"""
from typing import Any

euler_problem: int = 529
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 2}, 'answer': None},
    {'category': 'main', 'input': {'n': 18}, 'answer': None},
    {'category': 'extra', 'input': {'n': 20}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 234: Semidivisible Numbers.

Problem Statement:
    For an integer n >= 4, define the lower prime square root lps(n) as the largest
    prime <= sqrt(n), and the upper prime square root ups(n) as the smallest prime
    >= sqrt(n).

    Examples: lps(4) = 2 = ups(4). lps(1000) = 31, ups(1000) = 37.
    Call an integer n >= 4 semidivisible if one of lps(n) and ups(n) divides n,
    but not both.

    The sum of the semidivisible numbers not exceeding 15 is 30 (the numbers are
    8, 10 and 12). 15 is not semidivisible because it is a multiple of both
    lps(15) = 3 and ups(15) = 5. As a further example the sum of the 92
    semidivisible numbers up to 1000 is 34825.

    What is the sum of all semidivisible numbers not exceeding 999966663333?

URL: https://projecteuler.net/problem=234
"""
from typing import Any

euler_problem: int = 234
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 15}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 999966663333}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 710: One Million Members.

Problem Statement:
    On Sunday 5 April 2020 the Project Euler membership first exceeded one million
    members. We would like to present this problem to celebrate that milestone.
    Thank you to everyone for being a part of Project Euler.

    The number 6 can be written as a palindromic sum in exactly eight different
    ways:
        (1, 1, 1, 1, 1, 1), (1, 1, 2, 1, 1), (1, 2, 2, 1), (1, 4, 1),
        (2, 1, 1, 2), (2, 2, 2), (3, 3), (6)

    We shall define a twopal to be a palindromic tuple having at least one element
    with a value of 2. It should also be noted that elements are not restricted
    to single digits. For example, (3, 2, 13, 6, 13, 2, 3) is a valid twopal.

    If we let t(n) be the number of twopals whose elements sum to n, then it can
    be seen that t(6) = 4:
        (1, 1, 2, 1, 1), (1, 2, 2, 1), (2, 1, 1, 2), (2, 2, 2)

    Similarly, t(20) = 824.

    In searching for the answer to the ultimate question of life, the universe,
    and everything, it can be verified that t(42) = 1999923, which happens to be
    the first value of t(n) that exceeds one million.

    However, your challenge to the "ultimatest" question of life, the universe,
    and everything is to find the least value of n > 42 such that t(n) is divisible
    by one million.

URL: https://projecteuler.net/problem=710
"""
from typing import Any

euler_problem: int = 710
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'start_n': 43}, 'answer': None},
    {'category': 'main', 'input': {'start_n': 43}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

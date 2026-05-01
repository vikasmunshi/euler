#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 106: Special Subset Sums: Meta-testing.

Problem Statement:
    Let S(A) represent the sum of elements in set A of size n. We shall call it a
    special sum set if for any two non-empty disjoint subsets, B and C, the
    following properties are true:
        1. S(B) != S(C); that is, sums of subsets cannot be equal.
        2. If B contains more elements than C then S(B) > S(C).

    For this problem we shall assume that a given set contains n strictly increasing
    elements and it already satisfies the second rule.

    Surprisingly, out of the 25 possible subset pairs that can be obtained from a set
    for which n = 4, only 1 of these pairs need to be tested for equality (first rule).
    Similarly, when n = 7, only 70 out of the 966 subset pairs need to be tested.

    For n = 12, how many of the 261625 subset pairs that can be obtained need to be
    tested for equality?

URL: https://projecteuler.net/problem=106
"""
from typing import Any

euler_problem: int = 106
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 4}, 'answer': None},
    {'category': 'dev', 'input': {'n': 7}, 'answer': None},
    {'category': 'main', 'input': {'n': 12}, 'answer': None},
    {'category': 'extra', 'input': {'n': 16}, 'answer': None},
    {'category': 'extra', 'input': {'n': 32}, 'answer': None},
]
encrypted: str = (
    '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'
    'vtK9PJ3T7Eg='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

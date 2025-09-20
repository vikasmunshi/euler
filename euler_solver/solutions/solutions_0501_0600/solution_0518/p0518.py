#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 518: Prime Triples and Geometric Sequences.

Problem Statement:
    Let S(n) = sum a + b + c over all triples (a, b, c) such that:

        a, b and c are prime numbers.
        a < b < c < n.
        a+1, b+1, and c+1 form a geometric sequence.

    For example, S(100) = 1035 with the following triples:

        (2, 5, 11), (2, 11, 47), (5, 11, 23), (5, 17, 53),
        (7, 11, 17), (7, 23, 71), (11, 23, 47), (17, 23, 31),
        (17, 41, 97), (31, 47, 71), (71, 83, 97)

    Find S(10^8).

URL: https://projecteuler.net/problem=518
"""
from typing import Any

euler_problem: int = 518
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'WIh7lFawjX/KtJpXmMffew=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

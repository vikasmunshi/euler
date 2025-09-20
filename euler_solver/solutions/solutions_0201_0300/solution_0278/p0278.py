#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 278: Linear Combinations of Semiprimes.

Problem Statement:
    Given the values of integers 1 < a1 < a2 < ... < a_n, consider the linear
    combination q1 a1 + q2 a2 + ... + qn a_n = b, using only integer values q_k
    >= 0.
    Note that for a given set of a_k, it may be that not all values of b are
    possible. For instance, if a1 = 5 and a2 = 7, there are no q1 >= 0 and q2 >= 0
    such that b could be 1, 2, 3, 4, 6, 8, 9, 11, 13, 16, 18 or 23. In fact, 23 is
    the largest impossible value of b for a1 = 5 and a2 = 7. We therefore call
    f(5, 7) = 23. Similarly, it can be shown that f(6, 10, 15) = 29 and
    f(14, 22, 77) = 195.
    Find sum f(p*q, p*r, q*r), where p, q and r are prime numbers and
    p < q < r < 5000.

URL: https://projecteuler.net/problem=278
"""
from typing import Any

euler_problem: int = 278
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 30}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 5000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1000}, 'answer': None},
]
encrypted: str = (
    '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'
    'KgQSfU5GkLXT+yjF'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

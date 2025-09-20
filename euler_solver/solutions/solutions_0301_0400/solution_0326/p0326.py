#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 326: Modulo Summations.

Problem Statement:
    Let a_n be a sequence recursively defined by: a_1 = 1, and
    a_n = (sum_{k=1}^{n-1} k * a_k) mod n.

    So the first 10 elements of a_n are: 1, 1, 0, 3, 0, 3, 5, 4, 1, 9.

    Let f(N, M) represent the number of pairs (p, q) such that:
    1 <= p <= q <= N and (sum_{i=p}^q a_i) mod M = 0.

    It can be seen that f(10,10) = 4 with the pairs (3,3), (5,5), (7,9)
    and (9,10).

    You are also given that f(10^4,10^3) = 97158.

    Find f(10^12,10^6).

URL: https://projecteuler.net/problem=326
"""
from typing import Any

euler_problem: int = 326
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'N': 10, 'M': 10}, 'answer': None},
    {'category': 'main', 'input': {'N': 1000000000000, 'M': 1000000}, 'answer': None},
    {'category': 'extra', 'input': {'N': 1000000, 'M': 1000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

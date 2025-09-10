#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 127: abc-hits.

Problem Statement:
    The radical of n, rad(n), is the product of distinct prime factors of n.
    For example, 504 = 2^3 * 3^2 * 7, so rad(504) = 2 * 3 * 7 = 42.

    We shall define the triplet of positive integers (a, b, c) to be an abc-hit if:
        gcd(a, b) = gcd(a, c) = gcd(b, c) = 1
        a < b
        a + b = c
        rad(abc) < c

    For example, (5, 27, 32) is an abc-hit because:
        gcd(5,27) = gcd(5,32) = gcd(27,32) = 1
        5 < 27
        5 + 27 = 32
        rad(4320) = 30 < 32

    It turns out that abc-hits are rare and there are only thirty-one abc-hits
    for c < 1000, with sum c = 12523.

    Find sum c for c < 120000.

Solution Approach:
    Precompute rad(n) for all n up to the limit using a modified sieve (product of
    distinct prime factors). This is O(N log log N) preprocessing.
    For each c, iterate a from 1 to c//2 with gcd(a, c) = 1 (so b = c-a and a<b).
    Use precomputed rad to test whether rad(a) * rad(b) * rad(c) < c. Use fast
    gcd checks and skip candidates that share factors with c. Expected practical
    complexity roughly O(N log N) with careful pruning and integer arithmetic.

Answer: ...
URL: https://projecteuler.net/problem=127
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 127
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}},
    {'category': 'main', 'input': {'max_limit': 120000}},
    {'category': 'extra', 'input': {'max_limit': 200000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_abc_hits_p0127_s0(*, max_limit: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
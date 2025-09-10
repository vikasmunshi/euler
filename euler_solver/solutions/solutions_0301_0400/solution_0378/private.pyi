#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 378: Triangle Triples.

Problem Statement:
    Let T(n) be the n-th triangle number, so T(n) = n(n + 1)/2.
    Let dT(n) be the number of divisors of T(n).
    E.g.: T(7) = 28 and dT(7) = 6.

    Let Tr(n) be the number of triples (i, j, k) such that 1 <= i < j < k <= n
    and dT(i) > dT(j) > dT(k).
    Tr(20) = 14, Tr(100) = 5772, and Tr(1000) = 11174776.

    Find Tr(60000000).
    Give the last 18 digits of your answer.

Solution Approach:
    Compute dT(n) by factoring T(n) = n(n+1)/2 efficiently using a sieve of
    smallest prime factors and combining factorisations of n and n+1.
    Count strictly decreasing triples of dT values by treating each position j
    as the middle element: count left positions i<j with dT(i)>dT(j) and right
    positions k>j with dT(k)<dT(j), summing products.
    Use coordinate compression of dT values and Fenwick trees (BITs) for O(n
    log M) counting after O(n log log n) preprocessing. Take result mod 10^18.
    Expected complexity: roughly linearithmic in n with low-memory optimisations.

Answer: ...
URL: https://projecteuler.net/problem=378
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 378
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 20}},
    {'category': 'dev', 'input': {'n': 100}},
    {'category': 'main', 'input': {'n': 60000000}},
    {'category': 'extra', 'input': {'n': 1000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_triangle_triples_p0378_s0(*, n: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
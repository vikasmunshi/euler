#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 346: Strong Repunits.

Problem Statement:
    The number 7 is special, because 7 is 111 written in base 2, and 11
    written in base 6 (i.e. 7_10 = 11_6 = 111_2). In other words, 7 is a
    repunit in at least two bases b > 1.

    We shall call a positive integer with this property a strong repunit.
    It can be verified that there are 8 strong repunits below 50:
    {1, 7, 13, 15, 21, 31, 40, 43}.

    Furthermore, the sum of all strong repunits below 1000 equals 15864.

    Find the sum of all strong repunits below 10^12.

Solution Approach:
    Characterize repunits by R(k, b) = (b^k - 1) / (b - 1) for integers b > 1
    and k >= 2. For a fixed k, R(k, b) is increasing in b. Enumerate k up to
    floor(log2(limit + 1)) and, for each k, search integer bases b >= 2 while
    R(k, b) <= limit, computing R with exact integer arithmetic. Record each
    value and count how many distinct bases produce it; sum those with count
    >= 2. Use hashing to avoid duplicates and prune searches using bounds
    on b^k. Expected time roughly sum_k O(limit^{1/(k-1)}) with modest memory.

Answer: ...
URL: https://projecteuler.net/problem=346
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 346
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 50}},
    {'category': 'main', 'input': {'max_limit': 1000000000000}},
    {'category': 'extra', 'input': {'max_limit': 1000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_strong_repunits_p0346_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
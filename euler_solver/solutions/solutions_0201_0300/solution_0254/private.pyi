#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 254: Sums of Digit Factorials.

Problem Statement:
    Define f(n) as the sum of the factorials of the digits of n. For example,
    f(342) = 3! + 4! + 2! = 32.

    Define sf(n) as the sum of the digits of f(n). So sf(342) = 3 + 2 = 5.

    Define g(i) to be the smallest positive integer n such that sf(n) = i.
    Though sf(342) is 5, sf(25) is also 5, and it can be verified that g(5)
    is 25.

    Define sg(i) as the sum of the digits of g(i). So sg(5) = 2 + 5 = 7.

    Further, it can be verified that g(20) is 267 and sum sg(i) for 1 <= i <= 20
    is 156.

    What is sum sg(i) for 1 <= i <= 150?

Solution Approach:
    Precompute digit factorials 0!..9!. Observe f(n) depends only on digit counts.
    We need the minimal integer n (fewest digits, then lexicographically smallest)
    whose digit-factorial sum S has digit-sum sf(n)=i. Search over possible S
    values using DP/BFS mapping S -> minimal digit-multiset (cost: length+lexic).
    Compute sf(S) and aggregate sg(i) by converting chosen multiset to the minimal
    numeric n and summing its digits. Complexity depends on the S search bound;
    optimizations prune by numeric-cost and by limiting digit counts per value.

Answer: ...
URL: https://projecteuler.net/problem=254
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 254
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_i': 20}},
    {'category': 'main', 'input': {'max_i': 150}},
    {'category': 'extra', 'input': {'max_i': 500}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_sums_of_digit_factorials_p0254_s0(*, max_i: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
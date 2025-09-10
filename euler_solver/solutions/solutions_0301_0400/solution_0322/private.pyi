#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 322: Binomial Coefficients Divisible by 10.

Problem Statement:
    Let T(m, n) be the number of the binomial coefficients C(i, n) that are
    divisible by 10 for n <= i < m (i, m and n are positive integers).
    You are given that T(10^9, 10^7-10) = 989697000.

    Find T(10^18, 10^12-10).

Solution Approach:
    Use number theory and digit-DP. For a prime p, Lucas' theorem gives C(i,n)
    mod p from the base-p digits of i and n; C(i,n) is 0 mod p iff some
    digit of n exceeds the corresponding digit of i. Use this to count
    i in [n, m) for which C(i,n) is nonzero mod p by a digit-DP over base p.
    For divisibility by 10 require divisibility by both 2 and 5, so apply
    inclusion–exclusion combining counts for p=2 and p=5; implement digit-DP
    for each base and their joint constraints. Expected complexity about
    O(digits_base5 * digits_base2) ~ O(log m) with small constant factors.

Answer: ...
URL: https://projecteuler.net/problem=322
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 322
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'m': 1000000000, 'n': 9999990}},
    {'category': 'main', 'input': {'m': 1000000000000000000, 'n': 999999999990}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_binomial_coefficients_divisible_by_10_p0322_s0(*, m: int, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
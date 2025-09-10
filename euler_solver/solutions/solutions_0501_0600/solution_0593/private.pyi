#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 593: Fleeting Medians.

Problem Statement:
    We define two sequences S = {S(1), S(2), ..., S(n)} and S_2 = {S_2(1), S_2(2), ..., S_2(n)}:

    S(k) = (p_k)^k mod 10007 where p_k is the k-th prime number.

    S_2(k) = S(k) + S(floor(k/10000) + 1) where floor(·) denotes the floor function.

    Then let M(i, j) be the median of elements S_2(i) through S_2(j), inclusive.
    For example, M(1, 10) = 2021.5 and M(10^2, 10^3) = 4715.0.

    Let F(n, k) = sum_{i=1}^{n-k+1} M(i, i + k - 1).
    For example, F(100, 10) = 463628.5 and F(10^5, 10^4) = 675348207.5.

    Find F(10^7, 10^5). If the sum is not an integer, use .5 to denote a half. Otherwise, use .0
    instead.

Solution Approach:
    Utilize prime number generation and modular exponentiation to compute S efficiently.
    Exploit structure in S_2 sequence to avoid repeated calculations.
    For median computations on sliding windows, use data structures like balanced heaps or
    order statistics trees to achieve efficient median updates.
    Employ prefix sums or segment trees to accumulate F(n,k) efficiently.
    The main challenge is handling very large inputs (up to 10^7) within feasible time and memory.

Answer: ...
URL: https://projecteuler.net/problem=593
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 593
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 100, 'k': 10}},
    {'category': 'main', 'input': {'n': 10000000, 'k': 100000}},
    {'category': 'extra', 'input': {'n': 1000000, 'k': 10000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_fleeting_medians_p0593_s0(*, n: int, k: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
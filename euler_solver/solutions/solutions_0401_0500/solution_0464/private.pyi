#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 464: Möbius Function and Intervals.

Problem Statement:
    The Möbius function, denoted μ(n), is defined as:
        μ(n) = (-1)^ω(n) if n is squarefree (ω(n) is the number of distinct prime factors)
        μ(n) = 0 if n is not squarefree.

    Let P(a, b) be the number of integers n in [a, b] with μ(n) = 1.
    Let N(a, b) be the number of integers n in [a, b] with μ(n) = -1.
    For example, P(2,10) = 2 and N(2,10) = 4.

    Let C(n) be the number of integer pairs (a, b) with:
        1 ≤ a ≤ b ≤ n,
        99 * N(a, b) ≤ 100 * P(a, b), and
        99 * P(a, b) ≤ 100 * N(a, b).

    For example, C(10) = 13, C(500) = 16676, and C(10_000) = 20155319.

    Find C(20_000_000).

Solution Approach:
    Use number theory related to the Möbius function properties and squarefree integers.
    Precompute μ(n) for n up to 20 million using a sieve method.
    Use prefix sums of counts of μ(n) = 1 and μ(n) = -1 for quick range queries.
    Efficiently count pairs (a, b) using two-pointer or monotonic techniques under the ratio
    constraints. Expect to optimize and carefully handle large input for performance.

Answer: ...
URL: https://projecteuler.net/problem=464
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 464
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}},
    {'category': 'main', 'input': {'max_limit': 20000000}},
    {'category': 'extra', 'input': {'max_limit': 50000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_mobius_function_and_intervals_p0464_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
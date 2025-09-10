#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 745: Sum of Squares II.

Problem Statement:
    For a positive integer, n, define g(n) to be the maximum perfect square that
    divides n.

    For example, g(18) = 9, g(19) = 1.

    Also define
        S(N) = sum from n=1 to N of g(n).

    For example, S(10) = 24 and S(100) = 767.

    Find S(10^14). Give your answer modulo 1 000 000 007.

Solution Approach:
    Use number theory to deduce g(n) from the prime factorization of n as the
    product of prime powers squared. Summation reduces to counting over
    square divisors. Optimization likely involves Möbius inversion or
    inclusion-exclusion and efficient summation formulas.
    Expect O(N^(2/3)) or better with fast math techniques modulo 10^9+7.

Answer: ...
URL: https://projecteuler.net/problem=745
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 745
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}},
    {'category': 'main', 'input': {'max_limit': 10**14}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_sum_of_squares_ii_p0745_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
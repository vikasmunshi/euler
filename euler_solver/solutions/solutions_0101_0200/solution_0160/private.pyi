#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 160: Factorial Trailing Digits.

Problem Statement:
    For any N, let f(N) be the last five digits before the trailing zeroes in N!.
    For example,
    9! = 362880 so f(9)=36288
    10! = 3628800 so f(10)=36288
    20! = 2432902008176640000 so f(20)=17664

    Find f(1000000000000).

Solution Approach:
    Use number theory and modular arithmetic to compute the last five non-zero digits.
    Count and remove factors of 10 using exponents of 2 and 5 (Legendre formula).
    Compute the product of remaining terms modulo 100000, using periodicity and recursion
    that groups multiples of 5 and uses fast exponentiation and modular inverses.
    Time complexity: roughly O(log N) operations with small constant factors.
    Space complexity: O(1).

Answer: ...
URL: https://projecteuler.net/problem=160
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 160
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}},
    {'category': 'main', 'input': {'max_limit': 1000000000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_factorial_trailing_digits_p0160_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
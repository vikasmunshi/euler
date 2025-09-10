#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 248: Euler's Totient Function Equals 13!.

Problem Statement:
    The first number n for which phi(n) = 13! is 6227180929.
    Find the 150000th such number.

Solution Approach:
    Use inverse-totient enumeration based on the multiplicative property of phi.
    Let M = 13!. For any prime p dividing n, p-1 must divide M. Precompute primes
    p where (p-1) | M and consider prime powers p^e since phi(p^e)=p^{e-1}(p-1).
    Recursively assign factors of M to these prime-power contributions to build n.
    Generate all candidate n, sort them and select the n-th value. Use pruning,
    divisor enumeration and memoization to keep the search feasible (exponential
    in number of primes but small in practice for M = 13!).

Answer: ...
URL: https://projecteuler.net/problem=248
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 248
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 1}},
    {'category': 'main', 'input': {'n': 150000}},
    {'category': 'extra', 'input': {'n': 10000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_eulers_totient_function_equals_13_p0248_s0(*, n: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
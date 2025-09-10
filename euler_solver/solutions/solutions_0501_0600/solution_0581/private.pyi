#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 581: 47-smooth Triangular Numbers.

Problem Statement:
    A number is p-smooth if it has no prime factors larger than p.
    Let T be the sequence of triangular numbers, i.e. T(n) = n(n+1)/2.
    Find the sum of all indices n such that T(n) is 47-smooth.

Solution Approach:
    Use number theory and prime factorization to check smoothness efficiently.
    Triangular numbers come from product of two consecutive integers divided by 2.
    Factor n and n+1, combine factors, remove factor 2 once, then check max prime factor.
    Use sieve or prime factorization for primes up to 47.
    Sum all valid indices n. Expect complexity depends on factorization method.

Answer: ...
URL: https://projecteuler.net/problem=581
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 581
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_47_smooth_triangular_numbers_p0581_s0() -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
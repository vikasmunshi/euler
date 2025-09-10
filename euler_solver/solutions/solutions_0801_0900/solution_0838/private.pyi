#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 838: Not Coprime.

Problem Statement:
    Let f(N) be the smallest positive integer that is not coprime to any positive integer
    n ≤ N whose least significant digit is 3.

    For example f(40) equals to 897 = 3 · 13 · 23 since it is not coprime to any of 3, 13,
    23, 33. By taking the natural logarithm (log to base e) we obtain ln f(40) = ln 897
    ≈ 6.799056 when rounded to six digits after the decimal point.

    You are also given ln f(2800) ≈ 715.019337.

    Find f(10^6). Enter its natural logarithm rounded to six digits after the decimal point.

Solution Approach:
    Use number theory and prime factorization properties.
    Consider the set of numbers ending with digit 3 up to N, and ensure the constructed integer
    shares a common factor with each.
    Efficiently find the minimal integer with prime factors covering all such numbers.
    Use algorithms for factorization, least common multiples, and logarithm computations.
    Aim for efficient prime sieving and factor intersection for the problem scale.

Answer: ...
URL: https://projecteuler.net/problem=838
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 838
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 40}},
    {'category': 'main', 'input': {'max_limit': 1000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_not_coprime_p0838_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
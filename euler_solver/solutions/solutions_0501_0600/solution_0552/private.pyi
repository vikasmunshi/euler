#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 552: Chinese Leftovers II.

Problem Statement:
    Let A_n be the smallest positive integer satisfying A_n mod p_i = i for all 1 <= i <= n,
    where p_i is the i-th prime.

    For example A_2 = 5, since this is the smallest positive solution of the system of equations
        A_2 mod 2 = 1
        A_2 mod 3 = 2

    The system of equations for A_3 adds another constraint. That is, A_3 is the smallest positive
    solution of
        A_3 mod 2 = 1
        A_3 mod 3 = 2
        A_3 mod 5 = 3

    and hence A_3 = 23. Similarly, one gets A_4 = 53 and A_5 = 1523.

    Let S(n) be the sum of all primes up to n that divide at least one element in the sequence A.
    For example, S(50) = 69 = 5 + 23 + 41, since 5 divides A_2, 23 divides A_3 and 41 divides
    A_10 = 5765999453. No other prime number up to 50 divides an element in A.

    Find S(300000).

Solution Approach:
    Use number theory and modular arithmetic involving the Chinese remainder theorem.
    The problem involves solving simultaneous congruences and testing divisibility of large
    computed values by primes up to the given limit. Efficient prime generation and modular
    arithmetic techniques, potentially including optimizations on ranges and splitting tasks,
    will be critical for performance. Expected complexity depends heavily on prime generation and
    modular calculations.

Answer: ...
URL: https://projecteuler.net/problem=552
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 552
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 50}},
    {'category': 'main', 'input': {'max_limit': 300000}},
]

@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_chinese_leftovers_ii_p0552_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
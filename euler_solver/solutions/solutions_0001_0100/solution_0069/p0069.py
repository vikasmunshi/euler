#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 69: Totient Maximum.

Problem Statement:
    Euler's totient function, phi(n) [sometimes called the phi function], is defined as the
    number of positive integers not exceeding n which are relatively prime to n. For example,
    as 1, 2, 4, 5, 7, and 8, are all less than or equal to nine and relatively prime to nine,
    phi(9) = 6.

    It can be seen that n = 6 produces a maximum n/phi(n) for n ≤ 10.

    Find the value of n ≤ 1000000 for which n/phi(n) is a maximum.

Solution Approach:
    Use number theory properties of Euler's totient function.
    Maximize n/phi(n) by choosing n as product of small distinct primes.
    Iteratively multiply primes until limit is exceeded.
    Time complexity is efficient given small prime generation.

Answer: 510510
URL: https://projecteuler.net/problem=69
"""
from __future__ import annotations

from typing import Any

from euler_solver.framework import evaluate, logger, register_solution
from euler_solver.lib_primes import primes_generator

euler_problem: int = 69
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'limit': 10}, 'answer': 6},
    {'category': 'dev', 'input': {'limit': 100}, 'answer': 30},
    {'category': 'dev', 'input': {'limit': 1000}, 'answer': 210},
    {'category': 'dev', 'input': {'limit': 10000}, 'answer': 2310},
    {'category': 'dev', 'input': {'limit': 100000}, 'answer': 30030},
    {'category': 'main', 'input': {'limit': 1000000}, 'answer': 510510},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_totient_maximum_p0069_s0(*, limit: int) -> int:
    result: int = 1
    for prime_num in primes_generator():
        if (result := (result * prime_num)) > limit:
            result = result // prime_num
            break
    return result


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

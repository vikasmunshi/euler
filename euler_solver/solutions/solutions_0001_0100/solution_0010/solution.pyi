#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 10: Summation of Primes.

Problem Statement:
    The sum of the primes below 10 is 2 + 3 + 5 + 7 = 17.

    Find the sum of all the primes below two million.

Solution Approach:
    Use a prime sieve (e.g., Sieve of Eratosthenes) to efficiently find all primes below
    the given limit. Sum these primes. This approach runs in O(n log log n) time and uses
    O(n) space for the sieve.

Answer: ...
URL: https://projecteuler.net/problem=10
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 10
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'preliminary', 'input': {'max_num': 10}},
    {'category': 'main', 'input': {'max_num': 2000000}},
    {'category': 'extended', 'input': {'max_num': 10000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case=None)
def solve_summation_of_primes_p0010_s0(*, max_num: int) -> int:  # sundaram sieve
    ...

@register_solution(euler_problem=euler_problem, max_test_case=None)
def solve_summation_of_primes_p0010_s1(*, max_num: int) -> int:  # sundaram sieve
    ...

@register_solution(euler_problem=euler_problem, max_test_case=None)
def solve_summation_of_primes_p0010_s2(*, max_num: int) -> int:
    ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))

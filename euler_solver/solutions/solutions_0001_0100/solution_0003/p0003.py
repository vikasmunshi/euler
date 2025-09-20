#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 3: Largest Prime Factor.

Problem Statement:
    The prime factors of 13195 are 5, 7, 13 and 29.

    What is the largest prime factor of the number 600851475143?

Solution Approach:
    Use prime factorization by trial division starting from smallest primes.
    Efficiently reduce the number by dividing out smaller factors.
    Utilize the fact that largest prime factor <= sqrt(n).
    Expected complexity roughly O(sqrt(n)) in worst case.

Answer: 6857
URL: https://projecteuler.net/problem=3
"""
from __future__ import annotations

from typing import Any

from euler_solver.framework import evaluate, logger, register_solution

euler_problem: int = 3
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'number': 13195}, 'answer': 29},
    {'category': 'dev', 'input': {'number': 10}, 'answer': 5},
    {'category': 'dev', 'input': {'number': 20}, 'answer': 5},
    {'category': 'main', 'input': {'number': 600851475143}, 'answer': 6857},
    {'category': 'extra', 'input': {'number': 79376318561249}, 'answer': 9999991},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_largest_prime_factor_p0003_s0(*, number: int) -> int:
    if number % 2 == 0:
        remaining_number = reduce(number, 2)
        largest_factor = 2
    else:
        remaining_number = number
        largest_factor = 1
    current_factor = 3
    search_limit = int(remaining_number ** 0.5)
    while remaining_number > 1 and current_factor <= search_limit:
        if remaining_number % current_factor == 0:
            remaining_number = reduce(remaining_number, current_factor)
            largest_factor = current_factor
            search_limit = int(remaining_number ** 0.5)
        current_factor += 2
    return remaining_number if remaining_number > 1 else largest_factor


def reduce(num: int, divisor: int) -> int:
    num //= divisor
    while num % divisor == 0:
        num //= divisor
    return num


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

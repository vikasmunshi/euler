#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 23: Non-Abundant Sums.

Problem Statement:
    A perfect number is a number for which the sum of its proper divisors is exactly
    equal to the number. For example, the sum of the proper divisors of 28 would be
    1 + 2 + 4 + 7 + 14 = 28, which means that 28 is a perfect number.

    A number n is called deficient if the sum of its proper divisors is less than n and
    it is called abundant if this sum exceeds n.

    As 12 is the smallest abundant number, 1 + 2 + 3 + 4 + 6 = 16, the smallest number
    that can be written as the sum of two abundant numbers is 24. By mathematical
    analysis, it can be shown that all integers greater than 28123 can be written as
    the sum of two abundant numbers. However, this upper limit cannot be reduced any
    further by analysis even though it is known that the greatest number that cannot be
    expressed as the sum of two abundant numbers is less than this limit.

    Find the sum of all the positive integers which cannot be written as the sum of two
    abundant numbers.

Solution Approach:
    Identify abundant numbers via divisor sums using efficient divisor calculation.
    Use a boolean array to mark sums of two abundant numbers up to the limit.
    Sum numbers that cannot be represented as such. This combines number theory and
    optimized search with O(n^2) feasible due to the limit 28123.

Answer: 4179871
URL: https://projecteuler.net/problem=23
"""
from __future__ import annotations

from typing import Any

import numpy as np

from euler_solver.framework import evaluate, logger, register_solution
from euler_solver.lib_primes import sum_proper_divisors

euler_problem: int = 23
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': np.int64(4179871)},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_non_abundant_sums_p0023_s0() -> int:
    limit = 28123

    # Step 1: Precompute the sum of proper divisors for all numbers
    div_sums: np.ndarray = np.zeros(limit + 1, dtype=int)

    for i in range(1, limit // 2 + 1):
        div_sums[2 * i: limit + 1: i] += i

    # Step 2: Identify all abundant numbers
    abundant_numbers = np.flatnonzero(div_sums > np.arange(limit + 1))

    # Step 3: Mark all sums of two abundant numbers
    is_abundant_sum: np.ndarray = np.zeros(limit + 1, dtype=bool)

    for i in range(len(abundant_numbers)):
        sums = abundant_numbers[i] + abundant_numbers[i:]
        sums = sums[sums <= limit]
        is_abundant_sum[sums] = True

    # Step 4: Calculate the sum of all numbers that are not abundant sums
    non_abundant_sums = np.flatnonzero(~is_abundant_sum)
    return np.sum(non_abundant_sums)


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_non_abundant_sums_p0023_s1() -> int:
    limit = 28123

    # Find all abundant numbers
    abundant_numbers = [i for i in range(12, limit + 1) if sum_proper_divisors(i) > i]

    # Create a boolean array to mark sums of abundant numbers
    is_abundant_sum = [False] * (limit + 1)
    for i in range(len(abundant_numbers)):
        for j in range(i, len(abundant_numbers)):
            abundant_sum = abundant_numbers[i] + abundant_numbers[j]
            if abundant_sum > limit:
                break
            is_abundant_sum[abundant_sum] = True

    # Calculate the sum of all numbers that are not the sum of two abundant numbers
    return sum(i for i in range(1, limit + 1) if not is_abundant_sum[i])


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0023/p0023.py :: solve_non_abundant_sums_p0023_s0.

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
URL: https://projecteuler.net/problem=23"""
from __future__ import annotations

import numpy as np


def solve() -> int:
    limit = 28123
    div_sums: np.ndarray = np.zeros(limit + 1, dtype=int)
    for i in range(1, limit // 2 + 1):
        div_sums[2 * i:limit + 1:i] += i
    abundant_numbers = np.flatnonzero(div_sums > np.arange(limit + 1))
    is_abundant_sum: np.ndarray = np.zeros(limit + 1, dtype=bool)
    for i in range(len(abundant_numbers)):
        sums = abundant_numbers[i] + abundant_numbers[i:]
        sums = sums[sums <= limit]
        is_abundant_sum[sums] = True
    non_abundant_sums = np.flatnonzero(~is_abundant_sum)
    return int(np.sum(non_abundant_sums))


if __name__ == '__main__':
    print(solve())

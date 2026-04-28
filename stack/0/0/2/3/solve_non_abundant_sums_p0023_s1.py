#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0023/p0023.py :: solve_non_abundant_sums_p0023_s1.

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


def sum_proper_divisors(n: int) -> int:
    if n <= 1:
        return 0
    result = 1
    i = 2
    while i * i <= n:
        if n % i == 0:
            result += i
            if i != n // i:
                result += n // i
        i += 1
    return result


def solve() -> int:
    limit = 28123
    abundant_numbers = [i for i in range(12, limit + 1) if sum_proper_divisors(i) > i]
    is_abundant_sum = [False] * (limit + 1)
    for i in range(len(abundant_numbers)):
        for j in range(i, len(abundant_numbers)):
            abundant_sum = abundant_numbers[i] + abundant_numbers[j]
            if abundant_sum > limit:
                break
            is_abundant_sum[abundant_sum] = True
    return sum((i for i in range(1, limit + 1) if not is_abundant_sum[i]))


if __name__ == '__main__':
    print(solve())

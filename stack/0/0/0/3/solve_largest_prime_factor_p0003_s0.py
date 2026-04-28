#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0003/p0003.py :: solve_largest_prime_factor_p0003_s0.

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
URL: https://projecteuler.net/problem=3"""
from __future__ import annotations


def reduce(num: int, divisor: int) -> int:
    num //= divisor
    while num % divisor == 0:
        num //= divisor
    return num


def solve(*, number: int) -> int:
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


if __name__ == '__main__':
    import sys

    print(solve(number=int(sys.argv[1])))

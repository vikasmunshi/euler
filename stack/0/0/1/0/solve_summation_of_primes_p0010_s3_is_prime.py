#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0010/p0010.py :: solve_summation_of_primes_p0010_s3_is_prime.

Project Euler Problem 10: Summation of Primes.

Problem Statement:
    The sum of the primes below 10 is 2 + 3 + 5 + 7 = 17.

    Find the sum of all the primes below two million.

Solution Approach:
    Use a prime sieve (e.g., Sieve of Eratosthenes) to efficiently find all primes below
    the given limit. Sum these primes. This approach runs in O(n log log n) time and uses
    O(n) space for the sieve.

Answer: 142913828922
URL: https://projecteuler.net/problem=10"""
from __future__ import annotations


def is_prime(num: int) -> bool:
    if num < 2:
        return False
    if num == 2:
        return True
    if num % 2 == 0:
        return False
    i = 3
    while i * i <= num:
        if num % i == 0:
            return False
        i += 2
    return True


def solve(*, max_num: int) -> int:
    return sum((n for n in range(2, max_num) if is_prime(n)))


if __name__ == '__main__':
    import sys

    print(solve(max_num=int(sys.argv[1])))

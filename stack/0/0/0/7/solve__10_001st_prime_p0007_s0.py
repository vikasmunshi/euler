#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0007/p0007.py :: solve__10_001st_prime_p0007_s0.

Project Euler Problem 7: 10 001st Prime.

Problem Statement:
    By listing the first six prime numbers: 2, 3, 5, 7, 11, and 13, we can see that
    the 6th prime is 13.

    What is the 10 001st prime number?

Solution Approach:
    Use a prime sieving method or a prime checking algorithm to enumerate primes.
    Efficiently find the nth prime by dynamic sieving or probabilistic prime tests.
    Expected complexity depends on prime generation, typically near O(n log n) or better
    with segmented sieve optimizations.

Answer: 104743
URL: https://projecteuler.net/problem=7"""
from __future__ import annotations

from math import log


def solve(*, n: int) -> int:
    if n == 1:
        return 2
    max_expected_value = int(n * log(n))
    numbers = list(range(0, max_expected_value + 1))
    for i in numbers[1:]:
        for j in range(i, max_expected_value + 1):
            try:
                numbers[i + j + 2 * i * j] = 0
            except IndexError:
                break
    return 2 * [i for i in numbers if i != 0][n - 2] + 1


if __name__ == '__main__':
    import sys

    print(solve(n=int(sys.argv[1])))

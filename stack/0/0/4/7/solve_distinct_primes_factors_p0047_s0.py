#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0047/p0047.py :: solve_distinct_primes_factors_p0047_s0.

Project Euler Problem 47: Distinct Primes Factors.

Problem Statement:
    The first two consecutive numbers to have two distinct prime factors are:
        14 = 2 × 7
        15 = 3 × 5.

    The first three consecutive numbers to have three distinct prime factors are:
        644 = 2^2 × 7 × 23
        645 = 3 × 5 × 43
        646 = 2 × 17 × 19.

    Find the first four consecutive integers to have four distinct prime factors each.
    What is the first of these numbers?

Solution Approach:
    Use number theory and prime factorization techniques. Efficient prime factorization
    methods such as a sieve for smallest prime factors or trial division up to sqrt(n)
    help check the count of distinct prime factors per number. Search for consecutive
    integers meeting the condition. Expected complexity dominated by factorization cost.

Answer: 134043
URL: https://projecteuler.net/problem=47"""
from __future__ import annotations

from itertools import count


def prime_factorization(n: int) -> tuple[tuple[int, int], ...]:
    if n <= 1:
        return ()
    factors = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            exp = 0
            while n % d == 0:
                n //= d
                exp += 1
            factors.append((d, exp))
        d += 1
    if n > 1:
        factors.append((n, 1))
    return tuple(factors)


def prime_factor_count(n: int) -> int:
    return len(prime_factorization(n))


def solve(*, n: int) -> int:
    return next((number for number in count(2) if not any((prime_factor_count(number + i) != n for i in range(0, n)))))


if __name__ == '__main__':
    import sys

    print(solve(n=int(sys.argv[1])))

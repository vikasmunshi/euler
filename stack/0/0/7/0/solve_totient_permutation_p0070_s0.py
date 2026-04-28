#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0070/p0070.py :: solve_totient_permutation_p0070_s0.

Project Euler Problem 70: Totient Permutation.

Problem Statement:
    Euler's totient function, phi(n) [sometimes called the phi function], is used
    to determine the number of positive numbers less than or equal to n which are
    relatively prime to n. For example, as 1, 2, 4, 5, 7, and 8, are all less than
    nine and relatively prime to nine, phi(9)=6.
    The number 1 is considered to be relatively prime to every positive number, so
    phi(1)=1.

    Interestingly, phi(87109)=79180, and it can be seen that 87109 is a permutation
    of 79180.

    Find the value of n, 1 < n < 10^7, for which phi(n) is a permutation of n and
    the ratio n/phi(n) produces a minimum.

Solution Approach:
    Use number theory and combinatorics to compute phi(n) efficiently. Check
    permutations by digit comparison. Employ a sieve or factorization for phi
    calculations. Search space can be optimized considering properties of n and phi(n).
    Expected complexity involves prime factorization and permutation checks up to 10^7.

Answer: 8319823
URL: https://projecteuler.net/problem=70"""
from __future__ import annotations

from typing import Generator


def primes_generator() -> Generator[int, None, None]:
    yield 2
    composites: dict[int, int] = {}
    n = 3
    while True:
        if n not in composites:
            yield n
            composites[n * n] = n
        else:
            p = composites.pop(n)
            m = n + 2 * p
            while m in composites:
                m += 2 * p
            composites[m] = p
        n += 2


def solve(*, limit: int) -> int:
    min_ratio: float = float('inf')
    min_n: int = 0
    sqrt_n = int(limit ** 0.5)
    min_prime_1, max_prime_1 = (sqrt_n // 2, sqrt_n)
    for prime_1 in (p for p in primes_generator() if p > min_prime_1):
        if prime_1 > max_prime_1:
            break
        min_prime_2, max_prime_2 = (prime_1 + 2, int(limit / prime_1))
        for prime_2 in (p for p in primes_generator() if p > min_prime_2):
            if prime_2 > max_prime_2:
                break
            if sorted(str((number := (prime_1 * prime_2)))) == sorted(
                    str((totient := ((prime_1 - 1) * (prime_2 - 1))))):
                if (ratio := (number / totient)) < min_ratio:
                    min_ratio, min_n = (ratio, number)
    return min_n


if __name__ == '__main__':
    import sys

    print(solve(limit=int(sys.argv[1])))

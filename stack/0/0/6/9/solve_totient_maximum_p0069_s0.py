#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0069/p0069.py :: solve_totient_maximum_p0069_s0.

Project Euler Problem 69: Totient Maximum.

Problem Statement:
    Euler's totient function, phi(n) [sometimes called the phi function], is defined as the
    number of positive integers not exceeding n which are relatively prime to n. For example,
    as 1, 2, 4, 5, 7, and 8, are all less than or equal to nine and relatively prime to nine,
    phi(9) = 6.

    It can be seen that n = 6 produces a maximum n/phi(n) for n ≤ 10.

    Find the value of n ≤ 1000000 for which n/phi(n) is a maximum.

Solution Approach:
    Use number theory properties of Euler's totient function.
    Maximize n/phi(n) by choosing n as product of small distinct primes.
    Iteratively multiply primes until limit is exceeded.
    Time complexity is efficient given small prime generation.

Answer: 510510
URL: https://projecteuler.net/problem=69"""
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
    result: int = 1
    for prime_num in primes_generator():
        if (result := (result * prime_num)) > limit:
            result = result // prime_num
            break
    return result


if __name__ == '__main__':
    import sys

    print(solve(limit=int(sys.argv[1])))

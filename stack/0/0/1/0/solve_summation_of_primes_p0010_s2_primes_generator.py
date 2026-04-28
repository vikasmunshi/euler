#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0010/p0010.py

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


def solve(*, max_num: int) -> int:
    prime_number_gen = primes_generator()
    result: int = 0
    while (prime_number := next(prime_number_gen)) < max_num:
        result += prime_number
    return result


if __name__ == '__main__':
    import sys

    print(solve(max_num=int(sys.argv[1])))

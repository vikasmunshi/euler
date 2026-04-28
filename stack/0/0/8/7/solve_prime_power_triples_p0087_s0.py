#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0087/p0087.py :: solve_prime_power_triples_p0087_s0.

Project Euler Problem 87: Prime Power Triples.

Problem Statement:
    The smallest number expressible as the sum of a prime square, prime cube, and
    prime fourth power is 28. In fact, there are exactly four numbers below fifty
    that can be expressed in such a way:

        28 = 2^2 + 2^3 + 2^4
        33 = 3^2 + 2^3 + 2^4
        49 = 5^2 + 2^3 + 2^4
        47 = 2^2 + 3^3 + 2^4

    How many numbers below fifty million can be expressed as the sum of a prime
    square, prime cube, and prime fourth power?

Solution Approach:
    Use sieve of Eratosthenes to generate primes up to roughly sqrt(50 million).
    Enumerate sums of prime^2 + prime^3 + prime^4 below 50 million.
    Use sets for quick uniqueness and containment.
    This approach is efficient with optimized prime generation and pruning.

Answer: 1097343
URL: https://projecteuler.net/problem=87"""
from __future__ import annotations

from math import sqrt
from typing import Generator, Tuple


def prime_powers(primes: Tuple[int, ...], exponent: int) -> Generator[int, None, None]:
    for base in primes:
        yield (base ** exponent)


def primes_sundaram_sieve(max_num: int) -> tuple[int, ...]:
    if max_num < 2:
        return ()
    n = (max_num - 1) // 2
    marked = bytearray(n + 1)
    for i in range(1, n + 1):
        j = i
        while i + j + 2 * i * j <= n:
            marked[i + j + 2 * i * j] = 1
            j += 1
    primes = [2] if max_num >= 2 else []
    primes.extend((2 * i + 1 for i in range(1, n + 1) if not marked[i]))
    return tuple(primes)


def solve(*, max_num: int) -> int:
    primes: Tuple[int, ...] = primes_sundaram_sieve(int(sqrt(max_num)))
    numbers = set()
    max_quadruple_cube: int = max_num - 4
    max_quadruple: int = max_quadruple_cube - 8
    for quadruple in prime_powers(primes, 4):
        if quadruple > max_quadruple:
            break
        for cube in prime_powers(primes, 3):
            if (quadruple_cube := (quadruple + cube)) > max_quadruple_cube:
                break
            for square in prime_powers(primes, 2):
                if (number := (quadruple_cube + square)) >= max_num:
                    break
                numbers.add(number)
    return len(numbers)


if __name__ == '__main__':
    import sys

    print(solve(max_num=int(sys.argv[1])))

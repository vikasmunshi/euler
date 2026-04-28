#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0077/p0077.py :: solve_prime_summations_p0077_s0.

Project Euler Problem 77: Prime Summations.

Problem Statement:
    It is possible to write ten as the sum of primes in exactly five different ways:
    7 + 3
    5 + 5
    5 + 3 + 2
    3 + 3 + 2 + 2
    2 + 2 + 2 + 2 + 2

    What is the first value which can be written as the sum of primes in over five
    thousand different ways?

Solution Approach:
    Use dynamic programming to count partitions of integers into prime summands.
    Generate primes up to a suitable limit using a sieve. The count for each number
    can be computed from smaller numbers by adding primes recursively.
    The first integer with count > 5000 is the answer.
    Time complexity depends on the upper bound for search; DP with prime sieve is efficient.

Answer: 71
URL: https://projecteuler.net/problem=77"""
from __future__ import annotations

from functools import lru_cache
from itertools import count


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


@lru_cache(maxsize=None)
def num_prime_partitions_simple_recursion(*, number: int, slots: int) -> int:
    if number < 0 or slots < 0:
        raise ValueError('number and slots must be non-negative')
    if number == 0:
        return 1
    if slots < 2:
        return 0
    result = 0
    max_num = min(number, slots)
    for n in primes_sundaram_sieve(max_num):
        result += num_prime_partitions_simple_recursion(number=number - n, slots=n)
    return result


def solve(*, num_prime_partitions: int) -> int:
    for n in count(1):
        if num_prime_partitions_simple_recursion(number=n, slots=n) >= num_prime_partitions:
            return n
    return -1


if __name__ == '__main__':
    import sys

    sys.setrecursionlimit(10 ** 6)
    print(solve(num_prime_partitions=int(sys.argv[1])))

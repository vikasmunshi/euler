#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0050/p0050.py :: solve_consecutive_prime_sum_p0050_s0.

Project Euler Problem 50: Consecutive Prime Sum.

Problem Statement:
    The prime 41, can be written as the sum of six consecutive primes:
    41 = 2 + 3 + 5 + 7 + 11 + 13.
    This is the longest sum of consecutive primes that adds to a prime below
    one-hundred.

    The longest sum of consecutive primes below one-thousand that adds to a
    prime, contains 21 terms, and is equal to 953.

    Which prime, below one-million, can be written as the sum of the most
    consecutive primes?

Solution Approach:
    Use prime generation with a sieve (e.g., Sieve of Eratosthenes) up to the
    limit. Employ prefix sums for consecutive primes and check primality
    efficiently. A nested iteration over start and end indices with pruning
    will yield the longest consecutive prime sum. Expected complexity is near
    O(N log log N) for sieve plus O(N^2) in worst case for sums, reduced by
    pruning.

Answer: 997651
URL: https://projecteuler.net/problem=50"""
from __future__ import annotations

from itertools import accumulate
from typing import List, Set, Tuple


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


def solve(*, max_limit: int) -> int:
    primes_tuple: Tuple[int, ...] = primes_sundaram_sieve(max_limit)
    prime_sums: List[int] = [0] + list(accumulate(primes_tuple))
    primes: Set[int] = set(primes_tuple)
    number_of_primes_in_sum, prime = (0, 0)
    for i in range(number_of_primes_in_sum, len(prime_sums), 1):
        for j in range(i - number_of_primes_in_sum - 1, -1, -1):
            possible_prime = prime_sums[i] - prime_sums[j]
            if possible_prime > max_limit:
                break
            if possible_prime in primes:
                number_of_primes_in_sum = i - j
                prime = possible_prime
    return prime


if __name__ == '__main__':
    import sys

    print(solve(max_limit=int(sys.argv[1])))

#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 50: Consecutive Prime Sum [Level 2]. """
from __future__ import annotations

import itertools

from solver.runners import runner


def primes_sundaram_sieve(max_num: int) -> tuple[int, ...]:
    """Return all primes up to max_num via the Sieve of Sundaram; O(n log log n)."""
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


@runner.main
def solve(*args: str) -> str:
    """Prefix sums make each consecutive-prime sum one subtraction; two monotonicity prunes
    (break on exceeding the limit, skip runs no longer than the current best) keep the nominally
    quadratic search near-linear."""
    max_limit = runner.parse_int(args[0])

    primes_tuple: tuple[int, ...] = primes_sundaram_sieve(max_limit)
    prime_sums: list[int] = [0] + list(itertools.accumulate(primes_tuple))
    primes: set[int] = set(primes_tuple)
    number_of_primes_in_sum, prime = (0, 0)
    for i in range(number_of_primes_in_sum, len(prime_sums), 1):
        for j in range(i - number_of_primes_in_sum - 1, -1, -1):
            possible_prime = prime_sums[i] - prime_sums[j]
            if possible_prime > max_limit:
                break
            if possible_prime in primes:
                number_of_primes_in_sum = i - j
                prime = possible_prime
    return str(prime)


if __name__ == "__main__":
    raise SystemExit(solve())

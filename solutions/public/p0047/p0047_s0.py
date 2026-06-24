#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 47: Distinct Primes Factors [Level 1]. """
from __future__ import annotations

import itertools

from solver.runners import runner


def prime_factorization(n: int) -> tuple[tuple[int, int], ...]:
    """Factor n by trial division with in-place reduction, returning (prime, exponent) pairs; O(sqrt(n))."""
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
    """Number of distinct prime factors of n (the count of factorization pairs)."""
    return len(prime_factorization(n))


@runner.main
def solve(*args: str) -> str:
    """Linear scan for the first run of n consecutive integers each with n distinct prime factors.

    Each count is O(sqrt(k)) by trial division; the window test short-circuits via any() on the
    first failure, so the search costs about O(answer * sqrt(answer)).
    """
    n = runner.parse_int(args[0])

    return str(next(
        (number for number in itertools.count(2) if not any((prime_factor_count(number + i) != n for i in range(0, n))))
    ))


if __name__ == "__main__":
    raise SystemExit(solve())

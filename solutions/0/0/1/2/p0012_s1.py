#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 12: Highly Divisible Triangular Number [Level 0]. """
from __future__ import annotations

from solver.runners import runner


def prime_factorization(n: int) -> tuple[tuple[int, int], ...]:
    """Factor n by trial division to sqrt(n); return (prime, exponent) pairs."""
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


def num_factors(n: int) -> int:
    """Count divisors of n as the product of (exponent + 1) over its prime factors."""
    if n == 0:
        return 0
    result = 1
    for _, exp in prime_factorization(n):
        result *= exp + 1
    return result


@runner.main
def solve(*args: str) -> str:
    """Direct search: factor each whole triangular number T(i)=i(i+1)/2 by trial division
    and count its divisors until the count exceeds the target. O(sqrt(T(i))) per step."""
    num_divisors = runner.parse_int(args[0])

    i, triangle_number = (1, 1)
    while num_factors(triangle_number) < num_divisors:
        i += 1
        triangle_number = i * (i + 1) // 2
    return str(triangle_number)


if __name__ == "__main__":
    raise SystemExit(solve())

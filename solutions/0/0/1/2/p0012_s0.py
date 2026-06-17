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
    """Scan triangular numbers T(i)=i(i+1)/2; since gcd(i, i+1)=1, d(T(i)) is the product
    of the divisor counts of the two coprime halves (one carrying the /2), so each step
    factors numbers ~half of T(i). O(sqrt(T(i))) trial division per step."""
    num_divisors = runner.parse_int(args[0])

    i, triangle_number = (1, 1)
    while True:
        if i % 2 == 0:
            factors_i = num_factors(i // 2)
            factors_next = num_factors(i + 1)
        else:
            factors_i = num_factors(i)
            factors_next = num_factors((i + 1) // 2)
        divisor_count = factors_i * factors_next
        if divisor_count > num_divisors:
            return str(triangle_number)
        i += 1
        triangle_number = i * (i + 1) // 2


if __name__ == "__main__":
    raise SystemExit(solve())

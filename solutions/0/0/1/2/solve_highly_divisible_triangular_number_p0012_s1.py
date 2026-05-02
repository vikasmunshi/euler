#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0012/p0012.py
  func: solve_highly_divisible_triangular_number_p0012_s1
"""

from __future__ import annotations

from sys import argv


def prime_factorization(n: int) -> tuple[tuple[int, int], ...]:
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
    if n == 0:
        return 0
    result = 1
    for _, exp in prime_factorization(n):
        result *= exp + 1
    return result


def solve(*, num_divisors: int) -> int:
    i, triangle_number = (1, 1)
    while num_factors(triangle_number) < num_divisors:
        i += 1
        triangle_number = i * (i + 1) // 2
    return triangle_number


def main() -> int:
    print(solve(num_divisors=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

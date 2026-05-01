#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0047/p0047.py
  func: solve_distinct_primes_factors_p0047_s0
"""

from __future__ import annotations

from itertools import count
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


def prime_factor_count(n: int) -> int:
    return len(prime_factorization(n))


def solve(*, n: int) -> int:
    return next((number for number in count(2) if not any((prime_factor_count(number + i) != n for i in range(0, n)))))


def main() -> int:
    print(solve(n=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

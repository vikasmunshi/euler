#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0070/p0070.py
  func: solve_totient_permutation_p0070_s0
"""

from __future__ import annotations

from sys import argv
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


def solve(*, limit: int) -> int:
    min_ratio: float = float("inf")
    min_n: int = 0
    sqrt_n = int(limit**0.5)
    min_prime_1, max_prime_1 = (sqrt_n // 2, sqrt_n)
    for prime_1 in (p for p in primes_generator() if p > min_prime_1):
        if prime_1 > max_prime_1:
            break
        min_prime_2, max_prime_2 = (prime_1 + 2, int(limit / prime_1))
        for prime_2 in (p for p in primes_generator() if p > min_prime_2):
            if prime_2 > max_prime_2:
                break
            if sorted(str((number := (prime_1 * prime_2)))) == sorted(
                str((totient := ((prime_1 - 1) * (prime_2 - 1))))
            ):
                if (ratio := (number / totient)) < min_ratio:
                    min_ratio, min_n = (ratio, number)
    return min_n


def main() -> int:
    print(solve(limit=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

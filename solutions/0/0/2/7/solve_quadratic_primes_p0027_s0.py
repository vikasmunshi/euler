#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0027/p0027.py
  func: solve_quadratic_primes_p0027_s0
"""

from __future__ import annotations

from sys import argv


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


def is_prime(num: int) -> bool:
    if num < 2:
        return False
    if num == 2:
        return True
    if num % 2 == 0:
        return False
    i = 3
    while i * i <= num:
        if num % i == 0:
            return False
        i += 2
    return True


def prime_run(a: int, b: int) -> int:
    x = 0
    while is_prime(abs(x**2 + a * x + b)):
        x += 1
    return x


def solve(*, max_limit: int) -> int:
    return max(
        [
            max(
                (prime_run(a, b), a * b),
                (prime_run(a, -b), -a * b),
                (prime_run(-a, -b), a * b),
                (prime_run(-a, b), -a * b),
            )
            for b in primes_sundaram_sieve(max_limit)
            for a in range(0 if b == 2 else 1, max_limit, 2)
        ]
    )[1]


def main() -> int:
    print(solve(max_limit=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

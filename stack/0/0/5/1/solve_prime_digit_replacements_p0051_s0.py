#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0051/p0051.py
  func: solve_prime_digit_replacements_p0051_s0
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


def solve(*, num_digits: int, prime_run: int) -> int:
    for prime in primes_sundaram_sieve(10**num_digits):
        for replaced in "0123456789"[: 10 - prime_run]:
            sequence = tuple(
                (
                    new_prime
                    for replacement in "0123456789"
                    if replacement >= replaced
                    if (new_prime := int(str(prime).replace(replaced, replacement))) >= prime and is_prime(new_prime)
                )
            )
            if len(sequence) == prime_run:
                return prime
    else:
        raise ValueError("No solution found")


def main() -> int:
    print(solve(num_digits=int(argv[1]), prime_run=int(argv[2])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

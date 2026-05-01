#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0097/p0097.py
  func: solve_large_non_mersenne_prime_p0097_s0
"""

from __future__ import annotations

from sys import argv


def large_non_mersenne_prime(*, num_digits: int, prime: str) -> int:
    divisor: int = 10**num_digits
    prime_parts: list[str] = prime.split()
    number: int
    exponent: int
    number, exponent = (int(prime_parts[0]), int(prime_parts[2][2:]))
    for _ in range(exponent):
        number *= 2
        number %= divisor
    number += 1
    number %= divisor
    return number


def solve(*, num_digits: int, prime: str) -> int:
    return large_non_mersenne_prime(num_digits=num_digits, prime=prime)


def main() -> int:
    print(solve(num_digits=int(argv[1]), prime=str(argv[2])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

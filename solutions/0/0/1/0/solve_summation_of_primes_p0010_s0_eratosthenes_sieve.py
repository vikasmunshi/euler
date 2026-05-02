#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0010/p0010.py
  func: solve_summation_of_primes_p0010_s0_eratosthenes_sieve
"""

from __future__ import annotations

from sys import argv


def primes_eratosthenes_sieve_upto_max_num(max_num: int) -> tuple[int, ...]:
    if max_num < 2:
        return ()
    sieve = bytearray(b"\x01") * (max_num + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(max_num**0.5) + 1):
        if sieve[i]:
            sieve[i * i:: i] = bytearray(len(range(i * i, max_num + 1, i)))
    return tuple((i for i in range(2, max_num + 1) if sieve[i]))


def solve(*, max_num: int) -> int:
    return sum(primes_eratosthenes_sieve_upto_max_num(max_num))


def main() -> int:
    print(solve(max_num=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

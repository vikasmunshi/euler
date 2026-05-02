#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0010/p0010.py
  func: solve_summation_of_primes_p0010_s1_sundaram_sieve
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


def solve(*, max_num: int) -> int:
    return sum(primes_sundaram_sieve(max_num))


def main() -> int:
    print(solve(max_num=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

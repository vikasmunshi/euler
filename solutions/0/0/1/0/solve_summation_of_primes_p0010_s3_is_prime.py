#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0010/p0010.py
  func: solve_summation_of_primes_p0010_s3_is_prime
"""

from __future__ import annotations

from sys import argv


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


def solve(*, max_num: int) -> int:
    return sum((n for n in range(2, max_num) if is_prime(n)))


def main() -> int:
    print(solve(max_num=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

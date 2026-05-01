#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0010/p0010.py
  func: solve_summation_of_primes_p0010_s2_primes_generator
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


def solve(*, max_num: int) -> int:
    prime_number_gen = primes_generator()
    result: int = 0
    while (prime_number := next(prime_number_gen)) < max_num:
        result += prime_number
    return result


def main() -> int:
    print(solve(max_num=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0069/p0069.py
  func: solve_totient_maximum_p0069_s0
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
    result: int = 1
    for prime_num in primes_generator():
        if (result := (result * prime_num)) > limit:
            result = result // prime_num
            break
    return result


def main() -> int:
    print(solve(limit=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

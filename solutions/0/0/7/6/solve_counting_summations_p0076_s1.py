#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0076/p0076.py
  func: solve_counting_summations_p0076_s1
"""

from __future__ import annotations

from functools import lru_cache
from sys import argv, setrecursionlimit


@lru_cache(maxsize=None)
def num_partitions_simple_recursion(*, number: int, slots: int) -> int:
    if number < 0 or slots < 0:
        raise ValueError("number and slots must be non-negative")
    if number < slots:
        raise ValueError("number must be greater than or equal to slots")
    if number <= 1:
        return number
    return sum(
        (num_partitions_simple_recursion(number=number - n, slots=min(number - n, n)) for n in range(1, slots + 1))
    ) + (1 if number <= slots else 0)


def solve(*, num: int) -> int:
    return num_partitions_simple_recursion(number=num, slots=num) - 1


def main() -> int:
    setrecursionlimit(10**6)
    print(solve(num=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

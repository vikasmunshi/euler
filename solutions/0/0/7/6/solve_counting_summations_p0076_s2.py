#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0076/p0076.py
  func: solve_counting_summations_p0076_s2
"""

from __future__ import annotations

from functools import lru_cache
from sys import argv, setrecursionlimit


@lru_cache(maxsize=None)
def get_partitions_simple_recursion(*, number: int, slots: int, safe_limit: int | None = 50) -> list[list[int]]:
    if safe_limit and number > safe_limit:
        raise OverflowError(f"number must be less than safe_limit={safe_limit!r}")
    if number < 0 or slots < 0:
        raise ValueError("number and slots must be non-negative")
    if number < slots:
        raise ValueError("number must be greater than or equal to slots")
    if number <= 1:
        return [] if number == 0 else [[1]]
    partitions: list[list[int]] = []
    for n in range(1, slots + 1):
        if n == number:
            partitions.append([n])
        else:
            for partition in get_partitions_simple_recursion(
                number=number - n, slots=min(number - n, n), safe_limit=safe_limit
            ):
                partitions.append([n] + partition)
    for partition in partitions:
        assert sum(partition) == number, f"partition={partition!r} sum(partition)={sum(partition)!r} number={number!r}"
    return partitions


def solve(*, num: int) -> int:
    return len(get_partitions_simple_recursion(number=num, slots=num)) - 1


def main() -> int:
    setrecursionlimit(10**6)
    print(solve(num=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0076/p0076.py
  func: solve_counting_summations_p0076_s0
"""

from __future__ import annotations

from functools import lru_cache
from itertools import count
from sys import argv, setrecursionlimit


@lru_cache(maxsize=None)
def pentagonal(x: int) -> int:
    return x * (3 * x - 1) // 2


@lru_cache(maxsize=None)
def num_partitions_recursive_pentagonal(number: int) -> int:
    if number <= 0:
        result = int(number == 0)
        return result
    result = 0
    for n in count(1):
        p_1 = num_partitions_recursive_pentagonal(number - pentagonal(n))
        p_2 = num_partitions_recursive_pentagonal(number - pentagonal(-n))
        result += (-1, +1)[n % 2] * (p_1 + p_2)
        if p_1 == 0 and p_2 == 0:
            break
    return result


def solve(*, num: int) -> int:
    result: int = num_partitions_recursive_pentagonal(number=num) - 1
    return result


def main() -> int:
    setrecursionlimit(10**6)
    print(solve(num=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

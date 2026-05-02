#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0088/p0088.py
  func: solve_product_sum_numbers_p0088_s0
"""

from __future__ import annotations

from sys import argv, setrecursionlimit
from typing import List


def show_solution() -> bool:
    return "--show" in argv


def solve(*, max_k: int, min_k: int) -> int:
    max_k += 1
    min_prod: List[int] = [2 * max_k] * max_k

    def find_product_sum(prod: int, total: int, count: int, start: int) -> None:
        k = prod - total + count
        if k < max_k:
            min_prod[k] = min(min_prod[k], prod)
            for i in range(start, max_k // prod * 2 + 1):
                find_product_sum(prod * i, total + i, count + 1, i)

    find_product_sum(1, 1, 1, min_k)
    if show_solution():
        print(min_prod[2:])
    return sum(set(min_prod[2:]))


def main() -> int:
    setrecursionlimit(10**6)
    print(solve(max_k=int(argv[1]), min_k=int(argv[2])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

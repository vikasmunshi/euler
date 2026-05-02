#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0044/p0044.py
  func: solve_pentagon_numbers_p0044_s0
"""

from __future__ import annotations

from math import sqrt


def nth_pentagonal_number(n: int) -> int:
    return n * (3 * n - 1) // 2


def is_pentagonal_number(n: int) -> bool:
    return ((1 + sqrt(1 + 24 * n)) / 6).is_integer()


def solve() -> int:
    i = 0
    while i := (i + 1):
        p_i = nth_pentagonal_number(i)
        for j in range(i - 1, 0, -1):
            p_j = nth_pentagonal_number(j)
            if is_pentagonal_number(p_i - p_j) and is_pentagonal_number(p_i + p_j):
                return p_i - p_j
    else:
        raise ValueError("No solution found")


def main() -> int:
    print(solve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0073/p0073.py
  func: solve_counting_fractions_in_a_range_p0073_s2
"""

from __future__ import annotations

from sys import argv
from typing import List


def solve(*, max_d: int) -> int:

    def rank(n: int, d: int) -> int:
        len_data: int = max_d + 1
        data: List[int] = [i * n // d for i in range(len_data)]
        for i in range(1, len_data):
            for j in range(2 * i, len_data, i):
                data[j] -= data[i]
        return sum(data)

    return rank(n=1, d=2) - rank(n=1, d=3) - 1


def main() -> int:
    print(solve(max_d=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

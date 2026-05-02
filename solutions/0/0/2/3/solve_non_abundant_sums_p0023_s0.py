#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0023/p0023.py
  func: solve_non_abundant_sums_p0023_s0
"""

from __future__ import annotations

import numpy as np


def solve() -> int:
    limit = 28123
    div_sums: np.ndarray = np.zeros(limit + 1, dtype=int)
    for i in range(1, limit // 2 + 1):
        div_sums[2 * i: limit + 1: i] += i
    abundant_numbers = np.flatnonzero(div_sums > np.arange(limit + 1))
    is_abundant_sum: np.ndarray = np.zeros(limit + 1, dtype=bool)
    for i in range(len(abundant_numbers)):
        sums = abundant_numbers[i] + abundant_numbers[i:]
        sums = sums[sums <= limit]
        is_abundant_sum[sums] = True
    non_abundant_sums = np.flatnonzero(~is_abundant_sum)
    return int(np.sum(non_abundant_sums))


def main() -> int:
    print(solve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

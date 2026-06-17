#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 23: Non-Abundant Sums [Level 2]. """
from __future__ import annotations

import numpy as np
from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Sieve proper-divisor sums to flag abundant numbers, mark every pairwise sum of two
    abundant numbers, then sum the unmarked integers. Every integer above the fixed bound
    28123 is an abundant sum, so the search is finite. O(n log n) sieve, O(a^2) marking."""
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
    return str(int(np.sum(non_abundant_sums)))


if __name__ == "__main__":
    raise SystemExit(solve())

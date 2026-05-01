#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0007/p0007.py
  func: solve__10_001st_prime_p0007_s0
"""

from __future__ import annotations

from math import log
from sys import argv


def solve(*, n: int) -> int:
    if n == 1:
        return 2
    max_expected_value = int(n * log(n))
    numbers = list(range(0, max_expected_value + 1))
    for i in numbers[1:]:
        for j in range(i, max_expected_value + 1):
            try:
                numbers[i + j + 2 * i * j] = 0
            except IndexError:
                break
    return 2 * [i for i in numbers if i != 0][n - 2] + 1


def main() -> int:
    print(solve(n=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

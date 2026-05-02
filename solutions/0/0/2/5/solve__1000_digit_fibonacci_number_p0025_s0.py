#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0025/p0025.py
  func: solve__1000_digit_fibonacci_number_p0025_s0
"""

from __future__ import annotations

from sys import argv


def solve(*, n: int) -> int:
    a, b = (1, 1)
    i = 2
    while b < 10 ** (n - 1):
        a, b = (b, a + b)
        i += 1
    return i


def main() -> int:
    print(solve(n=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

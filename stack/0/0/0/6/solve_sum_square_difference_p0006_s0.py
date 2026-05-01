#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0006/p0006.py
  func: solve_sum_square_difference_p0006_s0
"""

from __future__ import annotations

from sys import argv


def solve(*, n: int) -> int:
    return (n * (n + 1) // 2) ** 2 - (2 * n + 1) * (n + 1) * n // 6


def main() -> int:
    print(solve(n=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

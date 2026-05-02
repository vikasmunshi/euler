#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0100/p0100.py
  func: solve_arranged_probability_p0100_s0
"""

from __future__ import annotations

from sys import argv


def solve(*, total_discs: int) -> int:
    x, y = (1, 1)
    while True:
        x, y = (3 * x + 4 * y, 2 * x + 3 * y)
        n = (x + 1) // 2
        b = (y + 1) // 2
        if n >= total_discs:
            return b


def main() -> int:
    print(solve(total_discs=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

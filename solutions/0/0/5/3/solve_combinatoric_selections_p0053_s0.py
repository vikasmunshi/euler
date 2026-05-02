#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0053/p0053.py
  func: solve_combinatoric_selections_p0053_s0
"""

from __future__ import annotations

from sys import argv


def solve(*, max_n: int, threshold: int) -> int:
    count = 0
    for n in range(1, max_n + 1):
        c = 1
        for r in range(0, n // 2 + 1):
            if c > threshold:
                count += n - 2 * r + 1
                break
            else:
                c = c * (n - r) // (r + 1)
    return count


def main() -> int:
    print(solve(max_n=int(argv[1]), threshold=int(argv[2])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0045/p0045.py
  func: solve_triangular_pentagonal_and_hexagonal_p0045_s0
"""

from __future__ import annotations

from sys import argv


def solve(*, n: int) -> int:
    while n := (n + 1):
        triangular_number = n * (n + 1) // 2
        if (1 + 24 * triangular_number) ** 0.5 % 6 == 5.0:
            if (1 + 8 * triangular_number) ** 0.5 % 4 == 3.0:
                return triangular_number
    else:
        raise ValueError("No solution found")


def main() -> int:
    print(solve(n=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

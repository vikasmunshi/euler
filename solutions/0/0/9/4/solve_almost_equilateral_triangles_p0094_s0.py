#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0094/p0094.py
  func: solve_almost_equilateral_triangles_p0094_s0
"""

from __future__ import annotations

from sys import argv


def solve(*, max_perimeter: int) -> int:
    s, s1, s2, m, p = (0, 1, 1, 1, 0)
    while p <= max_perimeter:
        s, s1, s2, m = (s + p, s2, 4 * s2 - s1 + 2 * m, -m)
        p = 3 * s2 - m
    return s


def main() -> int:
    print(solve(max_perimeter=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

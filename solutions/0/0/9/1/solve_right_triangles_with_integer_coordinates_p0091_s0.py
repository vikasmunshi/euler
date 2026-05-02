#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0091/p0091.py
  func: solve_right_triangles_with_integer_coordinates_p0091_s0
"""

from __future__ import annotations

from math import gcd
from sys import argv


def solve(*, coordinate_limit: int) -> int:
    triangles_at_p_or_q = sum(
        (
            min(x * m // y, m * (coordinate_limit - y) // x)
            for x in range(1, coordinate_limit + 1)
            for y in range(1, coordinate_limit)
            for m in [gcd(x, y)]
        )
    )
    triangles_at_p_or_q *= 2
    triangles_at_origin = 3 * coordinate_limit**2
    return triangles_at_p_or_q + triangles_at_origin


def main() -> int:
    print(solve(coordinate_limit=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
